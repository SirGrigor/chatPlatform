from sqlalchemy import Table, Column, Integer, ForeignKey

from db.base_class import Base

user_course_association = Table(
    'user_course_association', Base.metadata,
    Column('user_id', Integer, ForeignKey('external_users.id'), primary_key=True),
    Column('course_id', Integer, ForeignKey('courses.id'), primary_key=True)
)
