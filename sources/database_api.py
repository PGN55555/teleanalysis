from sqlalchemy import create_engine, Integer, String, Column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

from random import randint

DB_PATH = 'postgresql+psycopg2://bot:11111111@localhost:5428/msgdatabase'


class DataBase:
    Base = declarative_base()

    def __init__(self, db_path=DB_PATH) -> None:
        self.engine = create_engine(db_path)
        self.Base.metadata.create_all(self.engine)
        self.session = Session(bind=self.engine)

    class Messages(Base):
        __tablename__ = 'messages'
        id = Column(Integer(), primary_key=True)
        code = Column(Integer(), nullable=False)
        message = Column(String(), nullable=False)


    def add_message(self, message: str) -> int:
        code = randint(1000, 9999)
        while self.message_exists(code):
            code = randint(1000, 9999)
        
        msg = self.Messages(
            code = code,
            message=message
        )
        self.session.add(msg)
        self.session.new
        self.session.commit()
        
        return code

    def message_exists(self, code: int) -> bool:
        answer = self.get_message(code)
        return answer is not None

    def get_message(self, code: int):
        answer = self.session.query(self.Messages).filter(
            self.Messages.code == code).first()
        return answer
