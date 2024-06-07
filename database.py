import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, scoped_session

from dotenv import load_dotenv
#=====================================================

def _get_conn_string():
    _db_conn = os.getenv('DB_CONNECTION')
    _username = os.getenv('DB_USERNAME')
    _pass = os.getenv('DB_PASSWORD')
    _db_host = os.getenv('DB_HOST')
    _db_port = os.getenv('DB_PORT')
    _db_name = os.getenv('DB_DATABASE')
    _db_driver = os.getenv('DB_DRIVER')

    # str_conn = f"{_db_conn}+psycopg2://{_username}:{_pass}@{_db_host}:{_db_port}/{_db_name}"
    str_conn = f"{_db_conn}+{_db_driver}://{_username}:{_pass}@{_db_host}:{_db_port}/{_db_name}"
    return str_conn


def _create_pool_engine(size=10):
    str_conn = _get_conn_string()
    engine = create_engine(str_conn, pool_size=size, max_overflow=0)
    return engine

#=======================================================

load_dotenv()
db_engine = _create_pool_engine()
Base = declarative_base()

Session = sessionmaker(bind=db_engine, autocommit=False, autoflush=False)
def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()

class DbSession:
    def __init__(self):
        self.conn = db_engine.connect()
        self.session = scoped_session(sessionmaker(bind=db_engine, autocommit=False, autoflush=False))
    
    def __enter__(self):
        return self.session

    def __exit__(self, type, value, traceback):
        self.session.commit()
        self.session.close()
        self.conn.close()