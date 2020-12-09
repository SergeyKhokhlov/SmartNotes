import sqlalchemy
from .db_session import SqlAlchemyBase


class Note(SqlAlchemyBase):
    __tablename__ = 'Notes'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    folder_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    user_notes = sqlalchemy.Column(sqlalchemy.VARCHAR, nullable=True)