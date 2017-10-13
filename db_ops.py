import sqlalchemy
from model import *
from dateutil.relativedelta import relativedelta
from datetime import datetime


class DbOps(object):
    def __init__(self, egn):
        self.engine = egn
        self.session = scoped_session(sessionmaker(bind=self.engine))

    def set_loan(self, amount, term, rate, creation_date):
        """
        Create a new loan in the database.
        :param amount: amount of the Loan. INT.
        :param term: How long last the loan INT.
        :param rate: Rate of the loan. FLOAT.
        :param creation_date: Start time of the loan. DATETIME.
        :return: Loan object created in the DB
        :exception rollback
        :raise: sqlalchemy.exc.SQLAlchemyError, sqlalchemy.exc.DBAPIError
        """

        try:
            new_loan = Loan(amount=amount, term=term, rate=rate,
                            creation_date=creation_date)
            self.session.add(new_loan)
            self.session.commit()

            return new_loan

        except (sqlalchemy.exc.SQLAlchemyError, sqlalchemy.exc.DBAPIError) as e:
            self.session.rollback()
            raise

    def get_loan_by_id(self, uuid):
        """
        Method which will retrieve a loan by the given id
        :param id: id of the loan
        :return: the loan object
        :exception: return None
        """

        try:
            loan = self.session.query(Loan).get(UUID(uuid))
            if loan:
                return loan
            else:
                return None
        except (sqlalchemy.exc.SQLAlchemyError, sqlalchemy.exc.DBAPIError, ValueError):
            return None

    def set_payment(self, amount, loan_id, executed, date):
        """
        Create a new payment in the database.
        :param amount: amount paied.INT
        :param loan_id: ID of the loan. STR
        :param executed: accepted/refused BOOL
        :param date: date of the payment. DATETIME
        :return: the newly performed payment.
        :exception: Rollback DB transaction.
        :raise sqlalchemy.exc.SQLAlchemyError, sqlalchemy.exc.DBAPIError
        """

        loan = self.get_loan_by_id(loan_id)

        if loan:
            try:
                new_payment = Payment(amount=amount, loan_id=loan.id, executed=executed,
                                      date=date)
                self.session.add(new_payment)
                self.session.commit()
                return new_payment

            except (sqlalchemy.exc.SQLAlchemyError, sqlalchemy.exc.DBAPIError) as e:
                self.session.rollback()
                raise
        else:
            # return "No such Loan exists."
            return None

    def set_installment(self, Loan):
        """
          Compute the installment of a given loan.
        :param Loan: Loan object. See model.py.
        :return: The rounded (2) value of the loan.
        :raise: the arithmetical error
        """

        try:
            # formula : [ r + r / ( (1+r) ^ term - 1) ] x amount
            r = Loan.rate / 12
            installment = (r + r / ((1 + r) ** Loan.term - 1)) * Loan.amount
            return round(installment, 2)

        except ArithmeticError as e:
            # We log the error
            print(e)
            raise

    def get_debt_left(self, loan_id, date):

        # Get the loan with the given ID, with its start time and initial amount
        loan = self.get_loan_by_id(loan_id)

        if loan:

            # Calculate rest to pay at the given date.
            # calculate difference in month between given_date and end of payment ( start_date + term)
            # multiply months by monthly

            end_payment = loan.creation_date + relativedelta(months=loan.term)

            if loan.creation_date.timestamp() < date.timestamp() < end_payment.timestamp():
                diff_date_end = relativedelta(date.replace(tzinfo=None), end_payment)

                monthly_installment = self.set_installment(loan)
                rest_debt = monthly_installment * abs(diff_date_end.months)
                return rest_debt
            else:
                return None

        else:
            return None
