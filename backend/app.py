import os
from flask import Flask
from dotenv import load_dotenv
from extensions import db, migrate

load_dotenv()

"""
This file sets up the app, 
connects it to the database, 
wires in the database tools, 
and makes sure the schema-change system knows what tables you’ve defined.
"""

def create_app():
  app = Flask(__name__)

  app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
  app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

  app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-only")

  db.init_app(app)
  migrate.init_app(app, db)

  import models

  @app.get("/health")
  def health():
    return {"ok": True}
  
  return app

app = create_app()