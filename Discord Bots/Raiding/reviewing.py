from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey

Base = declarative_base()

engine = create_engine('sqlite:///reviews.db', echo=True)


# create a table for all users
class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    gamertag = Column(String)

    review_sent = relationship("Review", back_populates="reviewer")
    review_received = relationship("Review", back_populates="reviewee")


# create a table for reviews
class Review(Base):
    __tablename__ = 'review'

    id = Column(Integer, primary_key=True)
    text = Column(String)
    rating = Column(Integer)

    reviewer_id = Column(Integer, ForeignKey('user.id'))
    reviewer = relationship("User", back_populates="review_sent")

    reviewee_id = Column(Integer, ForeignKey('user.id'))
    reviewee = relationship("User", back_populates="review_received")
