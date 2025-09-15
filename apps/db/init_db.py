from apps.db.session import Base, engine
from apps.langgraph.models.quiz import QuizModel


def init_db():
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
