import json
from typing import Dict, List
from langchain_core.prompts import ChatPromptTemplate
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint


class LLMExtractor:
    def __init__(self, model: str = "mistralai/Mistral-7B-Instruct-v0.3"):
        """
        Extract job description features using HuggingFace model.
        """
        llm = HuggingFaceEndpoint(
            repo_id=model,
            temperature=0.1,
            max_new_tokens=512,
        )
        self.llm = ChatHuggingFace(llm=llm)

    def extract(self, text: str) -> Dict[str, List[str]]:
        """
        Use LLM to extract structured features from JD text.
        Returns dict with technical skills, soft skills, level, tools.
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an assistant that extracts computer science concepts from job descriptions."),
            ("human", """From the given job description, extract the relevant concepts and categorize them into the following subjects:

            - computer_network: networking concepts, technologies, or protocols (e.g., TCP/IP, DNS, HTTP, routing, firewalls).
            - data_structure_and_algorithm: fundamental data structures and algorithms (e.g., arrays, linked lists, binary trees, sorting, dynamic programming).
            - operating_system: operating system concepts (e.g., process scheduling, memory management, concurrency, Linux, Windows).

            Return ONLY JSON in the format:

            {{
            "computer_network": [...],
            "data_structure_and_algorithm": [...],
            "operating_system": [...]
            }}

            Job description:
            {jd_text}
            """)
        ])


        chain = prompt | self.llm
        response = chain.invoke({"jd_text": text})

        # parse JSON output
        try:
            data = json.loads(response.content)
        except json.JSONDecodeError:
            print("⚠️ Warning: Model output is not valid JSON. Raw output:")
            print(response.content)
            data = {}

        return data


if __name__ == "__main__":
    jd_text = """
        We are seeking a Backend Software Engineer to join our distributed systems team. 
        The ideal candidate will have strong foundations in computer science and be comfortable working with large-scale systems.

        Responsibilities:
        - Design and implement backend services for a high-traffic web application.
        - Optimize algorithms for search and data processing tasks.
        - Troubleshoot performance bottlenecks related to memory usage, CPU scheduling, and I/O handling in Linux environments.
        - Collaborate with the infrastructure team to ensure networking security and reliability across microservices.

        Requirements:
        - Proficiency in C++ or Java with strong problem-solving skills.
        - Deep knowledge of algorithms such as graph traversal, dynamic programming, and hashing.
        - Understanding of data structures including heaps, balanced binary trees, and hash tables.
        - Hands-on experience with TCP/IP, DNS, load balancers, and HTTP/HTTPS protocols.
        - Familiarity with operating system concepts: concurrency, deadlocks, threads vs processes, virtual memory, and scheduling algorithms.
        - Knowledge of distributed systems and caching strategies (Redis, Memcached) is a plus.
        - Strong communication skills and ability to work in agile teams.
    """
    extractor = LLMExtractor()
    result = extractor.extract(jd_text)
    print("✅ Extracted features:", result)
