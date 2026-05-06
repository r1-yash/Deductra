from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import User
from dotenv import load_dotenv
import os

load_dotenv()

engine = create_engine(os.getenv("DATABASE_URL"))
Session = sessionmaker(bind=engine)
db = Session()

# insert a test user
user = User(email="test@gmail.com", name="Yash")
db.add(user)
db.commit()
db.refresh(user)

print("User created:", user.id, user.email, user.name)

db.close()