# db/postgres.py
from sqlalchemy import create_engine, Column, Integer, String, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import yaml

# đọc config
config = yaml.safe_load(open("configs/config.yml"))
pg = config['postgresql']
DATABASE_URL = f"postgresql://{pg['user']}:{pg['password']}@{pg['host']}:{pg['port']}/{pg['database']}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Document(Base):
    __tablename__ = "vector_metadata"
    id = Column(String, primary_key=True, index=True)
    collection = Column(String, index=True)
    content = Column(Text)
    meta = Column(JSON)

def create_table():
    Base.metadata.create_all(engine)


if __name__ == "__main__":
    create_table()
    print("Table created!")