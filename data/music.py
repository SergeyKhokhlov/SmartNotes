import sqlalchemy
from .db_session import SqlAlchemyBase


class Musics(SqlAlchemyBase):
    __tablename__ = 'Music'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    file_id = sqlalchemy.Column(sqlalchemy.String, nullable=True)