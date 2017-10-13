# bank_challenge


1. Create a virtual environment with python >= 3 where to safely run the application.
2. cd bank_challenge; pip install -r requirements.txt
3. run python3 api.py.

* model.py: Contains the SQLAlchemy database classes, each of them is representation of a DB Table.
* db_ops.py: Contains a Class interacting with the database and performing actions on it.
* api.py: Contains the Flask api and as well the payload schema validators.
There is a class for each endpoint. It will also initiate a SQLite db  in the current folder.

As written in the mail, I took the liberty to make some small improvements, like replacing the 
payment "missed/made" by a scalar value (0/1), use the UUID format provided by the uuid library...) 