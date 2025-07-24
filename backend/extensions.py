from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask_jwt_extended import JWTManager

jwt = JWTManager()
DATABASE_URL = "mysql+pymysql://root:phi1osopher@localhost:3306/test0base"
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)