import os

class DevelopmentConfig(object):
  SECRET_KEY = os.environ.get("SECRETKEY")
  
