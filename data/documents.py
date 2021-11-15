import sqlalchemy
from .db_session import SqlAlchemyBase


class Document(SqlAlchemyBase):
    __tablename__ = 'Documents'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    file_id = sqlalchemy.Column(sqlalchemy.String, nullable=True)