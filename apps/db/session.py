from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

load_dotenv()


engine = create_engine(
    f"postgresql+psycopg2://{os.environ["POSTGRES_USER"]}:{os.environ["POSTGRES_PASSWORD"]}@{"127.0.0.1"}:{5432}",
    echo=True,
)

# session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, blind=engine)

Base = declarative_base()
