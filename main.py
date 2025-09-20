from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime, date, time
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Date, Time, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# --- DB Setup ---
DATABASE_URL = "sqlite:///./school.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# --- Models ---
class Student(Base):
    __tablename__ = "students"
    student_id = Column(String, primary_key=True)
    name = Column(String)
    interests = Column(String, nullable=True)
    attendance_percent = Column(Integer, default=0)

class Teacher(Base):
    __tablename__ = "teachers"
    teacher_id = Column(String, primary_key=True)
    name = Column(String)
    subject = Column(String)

class Class(Base):
    __tablename__ = "classes"
    class_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    subject = Column(String)
    teacher_id = Column(String, ForeignKey("teachers.teacher_id"))
    date = Column(Date)
    start_time = Column(Time)
    end_time = Column(Time)
    qr_code = Column(String)
    status = Column(String, default="ongoing")  # ongoing, completed, free

class Attendance(Base):
    __tablename__ = "attendance"
    attendance_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    class_id = Column(Integer, ForeignKey("classes.class_id"))
    student_id = Column(String, ForeignKey("students.student_id"))
    present = Column(Boolean, default=False)
    teacher_present = Column(Boolean, default=False)

class Timetable(Base):
    __tablename__ = "timetable"
    timetable_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    day_of_week = Column(String)  # Mon, Tue...
    subject = Column(String)
    teacher_id = Column(String, ForeignKey("teachers.teacher_id"))
    start_time = Column(Time)
    end_time = Column(Time)

class Score(Base):
    __tablename__ = "scores"
    score_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(String, ForeignKey("students.student_id"))
    subject = Column(String)
    marks = Column(Integer)

Base.metadata.create_all(bind=engine)

# --- FastAPI App ---
app = FastAPI()

# --- Schemas ---
class AttendanceIn(BaseModel):
    class_id: int
    student_id: Optional[str] = None

class EnterScoresIn(BaseModel):
    student_id: str
    scores: Dict[str, int]

# --- Dependencies ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Endpoints ---

# Teacher attendance
@app.put("/attendance/t")
def mark_teacher_attendance(data: AttendanceIn):
    db = next(get_db())
    cls = db.query(Class).filter(Class.class_id == data.class_id).first()
    if not cls:
        raise HTTPException(404, "Class not found")

    att = Attendance(class_id=data.class_id, teacher_present=True)
    db.add(att)
    db.commit()
    return {"status": "success", "message": "Teacher attendance marked", "class_id": data.class_id}

# Student attendance
@app.put("/attendance/s")
def mark_student_attendance(data: AttendanceIn):
    db = next(get_db())
    cls = db.query(Class).filter(Class.class_id == data.class_id).first()
    if not cls:
        raise HTTPException(404, "Class not found")

    att = Attendance(class_id=data.class_id, student_id=data.student_id, present=True)
    db.add(att)
    db.commit()
    return {"status": "success", "message": "Student attendance marked", "student_id": data.student_id}

# Suggestions (teacher view all)
@app.get("/suggestions/a")
def get_all_suggestions():
    db = next(get_db())
    students = db.query(Student).all()
    result = []
    for s in students:
        result.append({
            "student_id": s.student_id,
            "name": s.name,
            "top_suggestions": ["Math", "Physics", "Computer Science"]  # Stub
        })
    return {"status": "success", "students": result}

# Suggestions (student view)
@app.get("/suggestions/{student_id}")
def get_student_suggestions(student_id: str):
    return {
        "status": "success",
        "student_id": student_id,
        "top_suggestions": ["Math", "Physics", "Computer Science"]  # Stub
    }

# Timetable (student)
@app.get("/timetable/s/{student_id}")
def get_student_timetable(student_id: str):
    db = next(get_db())
    timetable = db.query(Timetable).all()
    return {"status": "success", "student_id": student_id, "timetable": [t.__dict__ for t in timetable]}

# Timetable (teacher)
@app.get("/timetable/t/{teacher_id}")
def get_teacher_timetable(teacher_id: str):
    db = next(get_db())
    timetable = db.query(Timetable).filter(Timetable.teacher_id == teacher_id).all()
    return {"status": "success", "teacher_id": teacher_id, "timetable": [t.__dict__ for t in timetable]}

# Scores (teacher all)
@app.get("/scores/t")
def get_all_scores():
    db = next(get_db())
    scores = db.query(Score).all()
    result = {}
    for s in scores:
        if s.student_id not in result:
            result[s.student_id] = {}
        result[s.student_id][s.subject] = s.marks
    return {"status": "success", "scores": result}

# Scores (student)
@app.get("/scores/{student_id}")
def get_student_scores(student_id: str):
    db = next(get_db())
    scores = db.query(Score).filter(Score.student_id == student_id).all()
    return {"status": "success", "student_id": student_id, "scores": {s.subject: s.marks for s in scores}}

# Enter Scores
@app.put("/enterscores")
def enter_scores(data: EnterScoresIn):
    db = next(get_db())
    for subject, marks in data.scores.items():
        score = Score(student_id=data.student_id, subject=subject, marks=marks)
        db.add(score)
    db.commit()
    return {"status": "success", "message": "Scores updated", "student_id": data.student_id, "scores": data.scores}

# Attendance View (teacher)
@app.get("/getattendance/t")
def get_all_attendance():
    db = next(get_db())
    records = db.query(Attendance).all()
    result = {}
    for r in records:
        if r.student_id not in result:
            result[r.student_id] = []
        result[r.student_id].append({
            "class_id": r.class_id,
            "present": r.present,
            "teacher_present": r.teacher_present
        })
    return {"status": "success", "attendance": result}

# Attendance View (student)
@app.get("/getattendance/{student_id}")
def get_student_attendance(student_id: str):
    db = next(get_db())
    records = db.query(Attendance).filter(Attendance.student_id == student_id).all()
    return {
        "status": "success",
        "student_id": student_id,
        "records": [{"class_id": r.class_id, "present": r.present} for r in records]
    }
