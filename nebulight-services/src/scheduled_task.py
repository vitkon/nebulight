# Import necessary modules
from sqlalchemy import create_engine, Column, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import uuid
from .models import Industry
from .database import engine

Session = sessionmaker(bind=engine)
session = Session()


def add_industry(name):
    new_industry = Industry(name=name)
    try:
        session.add(new_industry)
        session.commit()
        print(f"Industry '{name}' added successfully")
    except Exception as e:
        # session.rollback()
        print(f"Error adding industry: {e}")

def scheduled_task_handler(event=None, context=None):
    print('launch scheduled task')
    try:
        timestamp = datetime.utcnow()
        add_industry("test " + str(timestamp))
    except Exception as e:
        print(f"Error in scheduled task: {e}")


scheduled_task_handler()
