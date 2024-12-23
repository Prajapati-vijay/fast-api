from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from typing import List
from fastapi.responses import RedirectResponse

# Replace this with your actual connection string
DATABASE_URL = "mssql+pyodbc://SA:Vijay123456@sqlserver/student?driver=ODBC+Driver+17+for+SQL Server"

# Create the SQLAlchemy engine and session
engine = create_engine(DATABASE_URL, connect_args={"driver": "ODBC Driver 17 for SQL Server"})

# Create the sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Initialize FastAPI app
app = FastAPI()

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

@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    return RedirectResponse(url="/docs")

@app.get("/students", response_model=List[Student])
async def read_students(db: Session = Depends(get_db)):
    query = text("SELECT id, name, age, grade, city FROM students")  # Customize with your table name
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
