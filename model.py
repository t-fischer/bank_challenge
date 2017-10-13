from uuid import *
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import *
from sqlalchemy_utils.types import UUIDType

# We create the declarative base
Base = declarative_base()


class Loan(Base):
    """
      Class SQLAlchemy representing a loan.
      Has a one-to-many relationship with payment
    """
    __tablename__ = 'loans'

    id = Column(UUIDType, primary_key=True)
    amount = Column(Integer, nullable=False)
    term = Column(Integer, nullable=False)
    rate = Column(Integer, nullable=False)
    creation_date = Column(DateTime, nullable=False)

    payment_ = relationship('Payment', back_populates='loan_')

    def __init__(self, amount, term, rate, creation_date):
        self.amount = amount
        self.term = term
        self.rate = rate
        self.creation_date = creation_date
        self.id = uuid1()

    def __repr__(self):
        """print out nicely the object
        """
        return "<Loan(id='{}', amount='{}', term='{}', rate='{}',creation_date='{}' )>".format(self.id, self.amount,
                                                                                               self.term, self.rate,
                                                                                               self.creation_date)

    def to_dict(self):
        """
        generate a dictionary representation of the attributes of the class.

        Returns:
              dictionary of attributes
        """
        td = dict()

        for k, v in self.__dict__.items():
            if not k.startswith('_'):
                td[k] = v
        return td


class Payment(Base):
    """
      Class SQLAlchemy representing a payment of a Loan
    """

    __tablename__ = 'payments'

    id = Column(Integer, primary_key=True)
    loan_id = Column(UUIDType, ForeignKey('loans.id'), nullable=False)
    executed = Column(Boolean, nullable=False)
    amount = Column(Float, nullable=False)
    date = Column(DateTime, nullable=False)
    loan_ = relationship('Loan', back_populates='payment_')

    def __init__(self, id=None, amount=None, loan_id=None, executed=None, date=None):
        self.id = id
        self.amount = amount
        self.loan_id = loan_id
        self.executed = executed
        self.date = date

    def __repr__(self):
        """print out nicely the object
        """
        return "<Payment(id='{}', amount='{}', loan_id='{}', executed='{}',date='{}' )>".format(self.id, self.amount,
                                                                                                self.loan_id,
                                                                                                self.executed,
                                                                                                self.date)

    def to_dict(self):
        """
        generate a dictionary representation of the attributes of the class.

        Returns:
              dictionary of attributes
        """
        td = dict()

        for k, v in self.__dict__.items():
            if not k.startswith('_'):
                td[k] = v
        return td
