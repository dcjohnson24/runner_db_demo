import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    user = os.getenv('POSTGRES_USER')
    password = os.getenv('POSTGRES_PASSWORD')
    load_data = int(os.getenv('LOAD_DATA', '0'))
    if load_data:
        host = os.popen('docker-machine.exe ip').read().strip()
    # You need this one when running with docker-compose locally
    else:
        host = os.getenv('POSTGRES_HOST')
    database = os.getenv('POSTGRES_DB')
    port = os.getenv('POSTGRES_PORT')
    SQL_ALCHEMY_DATABASE_URI = (
        f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}'
    )


class TestConfig(Config):
    TESTING = True
    DEBUG = True
    WTF_CSRF_ENABLED = False
    host = os.popen('docker-machine.exe ip').read().strip()
    port = 5433
    SQL_ALCHEMY_DATABASE_URI = (
        f'postgresql+psycopg2://test_user:test_pass@'
        f'{host}:{port}/runner_test_db'
    )


class ProductionConfig:
    SQL_ALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
