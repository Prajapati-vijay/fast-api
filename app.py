from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from typing import List
from fastapi import Depends
from fastapi.middleware.cors import CORSMiddleware

# Replace this with your actual connection string
DATABASE_URL = "mssql+pyodbc://SA:vijay123@host.docker.internal/student?driver=ODBC+Driver+17+for+SQL+Server"

# Create the SQLAlchemy engine and session
engine = create_engine(DATABASE_URL, connect_args={"driver": "ODBC Driver 17 for SQL Server"})

# Create the sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Initialize FastAPI app
app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)
# Pydantic model for response
class Student(BaseModel):
    id: int
    name: str
    age: int
    grade: str
    city: str

    class Config:
        orm_mode = True  # Pydantic can read data from SQLAlchemy models

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/students", response_model=List[Student])
async def read_students(db: Session = Depends(get_db)):
    query = text("SELECT id, name, age, grade, city FROM students")  # Customize with your table name
    print("Getting data from API")
    try:
        # Execute the raw SQL query
        result = db.execute(query)
        # Fetch all rows as dictionaries
        rows = result.fetchall()  # Get all rows
        students = []
        
        for row in rows:
            # Convert each row into a dictionary and map to Pydantic model
            student = Student(**row._asdict())  # Convert row to dictionary and create Pydantic model
            students.append(student)

        return students
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
