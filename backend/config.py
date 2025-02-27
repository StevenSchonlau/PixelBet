from dotenv import load_dotenv
import os

load_dotenv(override=True)


class Config:
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://' + os.getenv("USER") + ':' + os.getenv("DB_PASSWORD") + '@' + os.getenv("HOST") + '/' + os.getenv("DATABASE")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('EMAIL_USERNAME', 'your_email@gmail.com')
    MAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', 'your_email_password')
    SERVER_URL = "http://localhost:5000/"