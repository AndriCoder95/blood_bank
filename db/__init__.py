from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app import app
import os
import sqlite3
from flask import g

# configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////tmp/test.db"
db = SQLAlchemy(app)
# import all models
from .models import user

# done only once!
# db.create_all()
