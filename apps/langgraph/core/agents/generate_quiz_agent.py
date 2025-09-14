from datetime import datetime
import os
import json
import random
from apps.helper.logger import LoggerSingleton
from apps.langgraph.core.agents.base_agent import BaseAgent
from langchain_core.prompts import ChatPromptTemplate
from langchain_aws import ChatBedrockConverse
from apps.langgraph.data.quiz import get_quiz, generate_quiz
from apps.db.session import SessionLocal
from dotenv import load_dotenv

load_dotenv()

logger = LoggerSingleton().get_instance()

MAX_ATTEMPTS = 2
MASTER_ROLE = "PRINCIPAL ENGINEER"
TRUTHY_VALUE = "CORRECT"
FALSY_VALUE = "INCORRECT"


random_seed = random.randint(0, 1000000)

INITIAL_MESSAGE_SYSTEM = "You are a helpful assistant."
INITIAL_MESSAGE_HUMAN = """
You are a {master_role}, you now give me one RANDOM quiz (with quiz random seed {random_seed} - do not put into the quiz) to test my skills in `{topic}` by typing one CLI command. Including a hint regarding how to solve such problem. Say all with me with a valid JSON format, starting with curly bracket, with properties:
The difficulty is {difficulty}
question: 'The question that based on the metric_score and the topic_base_difficulty.',
hint: 'A hint regarding how to solve such problem.'
    
After get answer from me, say exactly {truthy_value} or {falsy_value}, feedback on my answer and the correct detail answer with example outputs. Also, mark the matching percentage from my answer to the correct answer. Also, list the official related docs. Say all with me with a valid JSON format, starting with curly bracket, with properties:
correctness: '{truthy_value} || {falsy_value}',
answer: 'The correct detail CLI answer.',
feedback: 'A section for feedback or tips you want to say, based on the correct answer and my answer. Another section for the typical outputs (can be in multiline) put between <EXAMPLE_OUTPUT> and </EXAMPLE_OUTPUT>',
matching: 'A float value from 0.0 to 1.0 to compare the matching from my answer to the correct answer.',
references: 'Urls that may help me in the question.'
"""


def get_model():
    return ChatBedrockConverse(
        model_id=os.environ["BEDROCK_MODEL_NAME"],
        region_name=os.environ["BEDROCK_MODEL_REGION"],
        temperature=0.8,
        aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
    )


class GenQuizAgent(BaseAgent):
    def __init__(self, agent_name, llm, tools):
        super().__init__(agent_name, llm, tools)
        self.prompt = self.gen_quiz_agent_prompt()

    def gen_quiz_agent_prompt(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    INITIAL_MESSAGE_SYSTEM,
                ),
                (
                    "human",
                    INITIAL_MESSAGE_HUMAN,
                ),
            ]
        )

    @staticmethod
    def get_initial_history(
        master_role, random_seed, topic, difficulty, truthy_value, falsy_value
    ):
        return [
            ("system", INITIAL_MESSAGE_SYSTEM),
            (
                "human",
                INITIAL_MESSAGE_HUMAN.format(
                    master_role=master_role,
                    random_seed=random_seed,
                    topic=topic,
                    difficulty=difficulty,
                    truthy_value=truthy_value,
                    falsy_value=falsy_value,
                ),
            ),
        ]

    def generate_quiz(self, user_id: str, topic: str, difficulty: str) -> object:
        logger.debug(f"Generate quiz for user: {user_id}")
        try:
            messages = self.get_initial_history(
                MASTER_ROLE,
                random_seed,
                topic,
                difficulty,
                TRUTHY_VALUE,
                FALSY_VALUE,
            )
            chain = self.prompt | self.llm
            ai_msg = chain.invoke(
                {
                    "master_role": MASTER_ROLE,
                    "random_seed": random_seed,
                    "topic": topic,
                    "difficulty": difficulty,
                    "truthy_value": TRUTHY_VALUE,
                    "falsy_value": FALSY_VALUE,
                }
            )
            logger.debug(ai_msg)
            quiz = json.loads(ai_msg.content)
            logger.info(quiz)

            if "question" in quiz and "hint" in quiz:
                messages.append(
                    ("ai", f"question: {quiz['question']}. \nhint: {quiz['hint']}")
                )

            history = [{"role": role, "content": content} for role, content in messages]
            response = generate_quiz(
                history,
                quiz["question"],
                user_id,
                quiz["hint"],
                quiz.get("difficulty", difficulty),
                quiz.get("topic", topic),
            )
            # Save quiz
            with SessionLocal() as session:
                session.add(response)
                session.commit()
            return response
        except Exception as e:
            logger.error(f"Error for generating quiz for {user_id}: {str(e)}")

    def handle_answer_quiz(self, user_id: str, quiz_id: str, answer: str) -> object:
        if user_id is None or user_id.strip() == "":
            raise ValueError("user_id is required")
        if quiz_id is None or quiz_id.strip() == "":
            raise ValueError("quiz_id is required")
        if answer is None or answer.strip() == "":
            raise ValueError("answer is required")
        #
        try:
            quiz = get_quiz(quiz_id)
            if quiz is None:
                raise ValueError(f"Quiz not found with id: {quiz_id}")
        except Exception as e:
            raise ValueError(f"Error to get quiz by quiz_id: {quiz_id}. Error:{e}")

        conventional_history = quiz.history
        conventional_history.append({"role": "human", "content": answer})
        logger.info(f"Processing answer quiz with history: {conventional_history}")

        print("----------DEBUG-------------")
        prompt = ChatPromptTemplate.from_messages(conventional_history)

        chain = prompt | self.llm
        try:
            result = chain.invoke({})
            logger.info(f"LLM response: {result}")

            content = result.content

            if "<EXAMPLE_OUTPUT>" in content and "</EXAMPLE_OUTPUT>" in content:
                start = content.index("<EXAMPLE_OUTPUT>") + len("<EXAMPLE_OUTPUT>")
                end = content.index("</EXAMPLE_OUTPUT>")
                extracted_content = content[start:end].strip()

                content = (
                    content[: start - len("<EXAMPLE_OUTPUT>")].strip()
                    + content[end + len("</EXAMPLE_OUTPUT>") :].strip()
                )

                result_dict = json.loads(content)
                result_dict["feedback"] += "\n\n" + extracted_content
            else:
                result_dict = json.loads(content)

        except Exception as e:
            logger.error(f"Error invoking LLM: {str(e)}", exc_info=True)
            raise

        # Update
        quiz.answered_by_user_id = user_id
        quiz.user_answer = answer
        quiz.answer_date_created = datetime.now()
        quiz.status = "answered"
        quiz.answer_matching = float(result_dict.get("matching", 0.0))
        quiz.answer_feedback = result_dict.get("feedback", "")
        quiz.references = result_dict.get("references", [])
        if not isinstance(quiz.references, list):
            quiz.references = [quiz.references]
        quiz.correct_answer = result_dict.get("answer", "")
        quiz.history = conventional_history

        # Save quiz
        with SessionLocal() as session:
            session.add(quiz)
            session.commit()

        return quiz


