from dotenv import load_dotenv
import os


class Config:
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://' + os.getenv("USER") + ':' + os.getenv("DB_PASSWORD") + '@' + os.getenv("HOST") + '/' + os.getenv("DATABASE")
    SQLALCHEMY_TRACK_MODIFICATIONS = False