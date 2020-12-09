import sqlalchemy
from .db_session import SqlAlchemyBase


class Folder(SqlAlchemyBase):
    __tablename__ = 'Folders'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    names_folders = sqlalchemy.Column(sqlalchemy.VARCHAR, nullable=True)
    in_folder = sqlalchemy.Column(sqlalchemy.String, nullable=True)