import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


file_path = os.getcwd() + "/storage/storage.db"

engine = create_engine(f"sqlite:///{file_path}")
session = sessionmaker(bind=engine)








