import os

class DevelopmentConfig(object):
  SECRET_KEY = os.environ.get("SECRETKEY")
  
  SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:password123@localhost/mydb'
  SQLALCHEMY_TRACK_MODIFICATIONS = False
