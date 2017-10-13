from flask import *
from flask_restful import *
from marshmallow import *

from db_ops import DbOps
from model import *

# Initialize the application
app = Flask(__name__)
# We create a Blueprint to ease the url prefix handling and allow us further application extensions
api = Api(app, prefix='/loans')

# We are starting the SQLite
engine = create_engine('sqlite:///./bank_challenge.db', echo=False)
# We create the table in the database
Base.metadata.create_all(engine)
db_ops = DbOps(engine)


# Schema for validation/serialization of json objects
class LoanSchema(Schema):
    amount = fields.Integer(required=True)
    term = fields.Integer(required=True)
    rate = fields.Float(required=True)
    date = fields.DateTime(required=True, format='iso')


class PaymentSchema(Schema):
    amount = fields.Float(required=True)
    executed = fields.Boolean(required=True)
    date = fields.DateTime(required=True, format='iso')


class BalanceSchema(Schema):
    date = fields.DateTime(required=True, format='iso')


class LoansHandler(Resource):
    def post(self):

        json_data = request.get_json()

        if not json_data:
            return jsonify({'message': 'No input data provided'}), 400

        # Validate and deserialize input
        schema_loan = LoanSchema()
        data, errors = schema_loan.load(json_data)
        pprint(data)

        if errors:
            return errors

        try:
            inserted_loan = db_ops.set_loan(data['amount'], data['term'], data['rate'], data['date'])
            installment = db_ops.set_installment(inserted_loan)

            return jsonify({"loan_id": inserted_loan.id, "installment": installment})

        except Exception as e:
            # Remove details to hide the exception error from the API consumer
            return json.dump({"error": "Internal Server Error", "details": str(e)}), 500


class PaymentsHandler(Resource):
    """
     Class handling the payments requests.
    """

    def post(self, id):

        json_data = request.get_json()

        if not json_data:
            return jsonify({'message': 'No input data provided'}), 400

        # Validate and deserialize input
        schema_payment = PaymentSchema()
        data, errors = schema_payment.load(json_data)

        if errors:
            return errors

        try:
            payment = db_ops.set_payment(amount=data['amount'], executed=data['executed'], date=data['date'],
                                         loan_id=id)
            # Dumps the newly created payment to a JSON object
            payment_dumps = schema_payment.dump(payment)
            return payment_dumps

        except Exception as e:
            # Remove details to hide the exception error from the API consumer
            return json.dump({'error': 'Internal Server Error', 'details': str(e)}), 500


class BalanceHandler(Resource):
    def post(self, id):
        json_data = request.get_json()

        if not json_data:
            return jsonify({'message': 'No input data provided'}), 400

        # Validate and deserialize input
        schema_balance = BalanceSchema()
        data, errors = schema_balance.load(json_data)

        if errors:
            return errors

        try:
            debt_left = db_ops.get_debt_left(loan_id=id, date=data['date'])

            # Dumps the newly created payment to a JSON object
            return jsonify({"balance": debt_left})
        except Exception as e:
            # Remove details to hide the exception error from the API consumer
            return jsonify({'error': 'Internal Server Error', 'details': str(e)}), 500


# Linking the routes to proper calls
api.add_resource(LoansHandler, '/')
api.add_resource(PaymentsHandler, '/<string:id>/payments')
api.add_resource(BalanceHandler, '/<string:id>/balance')

# Start the application
if __name__ == '__main__':
    # We start the web application
    app.run(debug=True, port=5000)
