from flask_sqlalchemy import SQLAlchemy

sql_db = SQLAlchemy()


class User(sql_db.Model):
    username = sql_db.Column(sql_db.String,
                             primary_key=True,
                             unique=True,
                             nullable=False)
    email = sql_db.Column(sql_db.String)
    current_room = sql_db.Column(sql_db.Integer, nullable=True)
