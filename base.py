import sqlalchemy as sq
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import Session
from tokens import DSN

metadata = MetaData()

Base = declarative_base()


class Users(Base):
    __tablename__ = 'users'

    profile_id = sq.Column(sq.Integer, primary_key=True)
    worksheet_id = sq.Column(sq.Integer, primary_key=True)


def add_user(engine, profile_id, worksheet_id):
    with Session(engine) as session:
        to_bd = Users(profile_id=profile_id, worksheet_id=worksheet_id)
        session.add(to_bd)
        session.commit()


def check_user(engine, profile_id, worksheet_id):
    with Session(engine) as session:
        from_bd = session.query(Users).filter(
            Users.profile_id == profile_id,
            Users.worksheet_id == worksheet_id
        ).first()
        return True if from_bd else False


if __name__ == '__main__':
    engine = create_engine(DSN)
    Base.metadata.create_all(engine)
    



