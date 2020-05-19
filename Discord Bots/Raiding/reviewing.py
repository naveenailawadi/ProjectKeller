from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey

Base = declarative_base()
engine = create_engine('sqlite:///reviews.db', echo=True)

Session = sessionmaker()
Session.configure(bind=engine)

session = Session()


# create a table for all users
class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    gamertag = Column(String)


# create a table for reviews
class Review(Base):
    __tablename__ = 'review'

    id = Column(Integer, primary_key=True)
    text = Column(String, default=None)
    rating = Column(Integer)

    reviewer_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    reviewer = relationship("User", foreign_keys=[reviewer_id])

    reviewee_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    reviewee = relationship("User", foreign_keys=[reviewee_id])
