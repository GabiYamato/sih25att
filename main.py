# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# from typing import List, Dict, Optional
# from datetime import datetime, date, time
# from sqlalchemy import create_engine, Column, Integer, String, Boolean, Date, Time, ForeignKey, Enum
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker, relationship
# import os
# from dotenv import load_dotenv

# # Load environment variables
# load_dotenv()

# # --- DB Setup ---
# DATABASE_URL = os.getenv("DATABASE_URL")

# engine = create_engine(DATABASE_URL)
# Base = declarative_base()
# SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# # --- Models ---
# class Student(Base):
#     __tablename__ = "students"
#     student_id = Column(String(50), primary_key=True)
#     name = Column(String(100))
#     interests = Column(String(500), nullable=True)
#     attendance_percent = Column(Integer, default=0)

# class Teacher(Base):
#     __tablename__ = "teachers"
#     teacher_id = Column(String(50), primary_key=True)
#     name = Column(String(100))
#     subject = Column(String(100))

# class Class(Base):
#     __tablename__ = "classes"
#     class_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
#     subject = Column(String(100))
#     teacher_id = Column(String(50), ForeignKey("teachers.teacher_id"))
#     date = Column(Date)
#     start_time = Column(Time)
#     end_time = Column(Time)
#     qr_code = Column(String(100))
#     status = Column(String(20), default="ongoing")  # ongoing, completed, free

# class Attendance(Base):
#     __tablename__ = "attendance"
#     attendance_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
#     class_id = Column(Integer, ForeignKey("classes.class_id"))
#     student_id = Column(String(50), ForeignKey("students.student_id"))
#     present = Column(Boolean, default=False)
#     teacher_present = Column(Boolean, default=False)

# class Timetable(Base):
#     __tablename__ = "timetable"
#     timetable_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
#     day_of_week = Column(String(10))  # Mon, Tue...
#     subject = Column(String(100))
#     teacher_id = Column(String(50), ForeignKey("teachers.teacher_id"))
#     start_time = Column(Time)
#     end_time = Column(Time)

# class Score(Base):
#     __tablename__ = "scores"
#     score_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
#     student_id = Column(String(50), ForeignKey("students.student_id"))
#     subject = Column(String(100))
#     marks = Column(Integer)

# Base.metadata.create_all(bind=engine)

# # --- FastAPI App ---
# app = FastAPI()

# # --- Schemas ---
# class AttendanceIn(BaseModel):
#     class_id: int
#     student_id: Optional[str] = None

# class EnterScoresIn(BaseModel):
#     student_id: str
#     scores: Dict[str, int]

# # --- Dependencies ---
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# # --- Endpoints ---

# # Teacher attendance
# @app.put("/attendance/t")
# def mark_teacher_attendance(data: AttendanceIn):
#     db = next(get_db())
#     cls = db.query(Class).filter(Class.class_id == data.class_id).first()
#     if not cls:
#         raise HTTPException(404, "Class not found")

#     att = Attendance(class_id=data.class_id, teacher_present=True)
#     db.add(att)
#     db.commit()
#     return {"status": "success", "message": "Teacher attendance marked", "class_id": data.class_id}

# # Student attendance
# @app.put("/attendance/s")
# def mark_student_attendance(data: AttendanceIn):
#     db = next(get_db())
#     cls = db.query(Class).filter(Class.class_id == data.class_id).first()
#     if not cls:
#         raise HTTPException(404, "Class not found")

#     att = Attendance(class_id=data.class_id, student_id=data.student_id, present=True)
#     db.add(att)
#     db.commit()
#     return {"status": "success", "message": "Student attendance marked", "student_id": data.student_id}

# # Suggestions (teacher view all)
# @app.get("/suggestions/a")
# def get_all_suggestions():
#     db = next(get_db())
#     students = db.query(Student).all()
#     result = []
#     for s in students:
#         result.append({
#             "student_id": s.student_id,
#             "name": s.name,
#             "top_suggestions": ["Math", "Physics", "Computer Science"]  # Stub
#         })
#     return {"status": "success", "students": result}

# # Suggestions (student view)
# @app.get("/suggestions/{student_id}")
# def get_student_suggestions(student_id: str):
#     return {
#         "status": "success",
#         "student_id": student_id,
#         "top_suggestions": ["Math", "Physics", "Computer Science"]  # Stub
#     }

# # Timetable (student)
# @app.get("/timetable/s/{student_id}")
# def get_student_timetable(student_id: str):
#     db = next(get_db())
#     timetable = db.query(Timetable).all()
#     return {"status": "success", "student_id": student_id, "timetable": [t.__dict__ for t in timetable]}

# # Timetable (teacher)
# @app.get("/timetable/t/{teacher_id}")
# def get_teacher_timetable(teacher_id: str):
#     db = next(get_db())
#     timetable = db.query(Timetable).filter(Timetable.teacher_id == teacher_id).all()
#     return {"status": "success", "teacher_id": teacher_id, "timetable": [t.__dict__ for t in timetable]}

# # Scores (teacher all)
# @app.get("/scores/t")
# def get_all_scores():
#     db = next(get_db())
#     scores = db.query(Score).all()
#     result = {}
#     for s in scores:
#         if s.student_id not in result:
#             result[s.student_id] = {}
#         result[s.student_id][s.subject] = s.marks
#     return {"status": "success", "scores": result}

# # Scores (student)
# @app.get("/scores/{student_id}")
# def get_student_scores(student_id: str):
#     db = next(get_db())
#     scores = db.query(Score).filter(Score.student_id == student_id).all()
#     return {"status": "success", "student_id": student_id, "scores": {s.subject: s.marks for s in scores}}

# # Enter Scores
# @app.put("/enterscores")
# def enter_scores(data: EnterScoresIn):
#     db = next(get_db())
#     for subject, marks in data.scores.items():
#         score = Score(student_id=data.student_id, subject=subject, marks=marks)
#         db.add(score)
#     db.commit()
#     return {"status": "success", "message": "Scores updated", "student_id": data.student_id, "scores": data.scores}

# # Attendance View (teacher)
# @app.get("/getattendance/t")
# def get_all_attendance():
#     db = next(get_db())
#     records = db.query(Attendance).all()
#     result = {}
#     for r in records:
#         if r.student_id not in result:
#             result[r.student_id] = []
#         result[r.student_id].append({
#             "class_id": r.class_id,
#             "present": r.present,
#             "teacher_present": r.teacher_present
#         })
#     return {"status": "success", "attendance": result}

# # Attendance View (student)
# @app.get("/getattendance/{student_id}")
# def get_student_attendance(student_id: str):
#     db = next(get_db())
#     records = db.query(Attendance).filter(Attendance.student_id == student_id).all()
#     return {
#         "status": "success",
#         "student_id": student_id,
#         "records": [{"class_id": r.class_id, "present": r.present} for r in records]
#     }



from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime, date, time
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Date, Time, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os
from dotenv import load_dotenv
# import qrcode
# import io
# import base64
# from PIL import Image

# Load environment variables
load_dotenv()

# --- DB Setup ---
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# --- Models ---
class Student(Base):
    __tablename__ = "students"
    student_id = Column(String(50), primary_key=True)
    name = Column(String(100))
    interests = Column(String(500), nullable=True)
    attendance_percent = Column(Integer, default=0)

class Teacher(Base):
    __tablename__ = "teachers"
    teacher_id = Column(String(50), primary_key=True)
    name = Column(String(100))
    subject = Column(String(100))

class Class(Base):
    __tablename__ = "classes"
    class_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    subject = Column(String(100))
    teacher_id = Column(String(50), ForeignKey("teachers.teacher_id"))
    date = Column(Date)
    start_time = Column(Time)
    end_time = Column(Time)
    qr_code = Column(String(100))
    status = Column(String(20), default="ongoing")  # ongoing, completed, free

class Attendance(Base):
    __tablename__ = "attendance"
    attendance_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    class_id = Column(Integer, ForeignKey("classes.class_id"))
    student_id = Column(String(50), ForeignKey("students.student_id"))
    present = Column(Boolean, default=False)
    teacher_present = Column(Boolean, default=False)

class Timetable(Base):
    __tablename__ = "timetable"
    timetable_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    day_of_week = Column(String(10))  # Mon, Tue...
    subject = Column(String(100))
    teacher_id = Column(String(50), ForeignKey("teachers.teacher_id"))
    start_time = Column(Time)
    end_time = Column(Time)

class Score(Base):
    __tablename__ = "scores"
    score_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(String(50), ForeignKey("students.student_id"))
    subject = Column(String(100))
    marks = Column(Integer)

Base.metadata.create_all(bind=engine)

# --- FastAPI App ---
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server
        "http://localhost:5173",  # Vite dev server
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "https://4fz7ztsn-8000.inc1.devtunnels.ms",  # Your tunnel domain
        "*"  # Allow all origins for development (remove in production)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Schemas ---
class AttendanceIn(BaseModel):
    class_id: int
    student_id: Optional[str] = None

class EnterScoresIn(BaseModel):
    student_id: str
    scores: Dict[str, int]

# Pydantic models for request/response
class StudentLoginIn(BaseModel):
    student_id: str
    password: str

class QRCodeRequest(BaseModel):
    class_id: int
    teacher_id: str
    
class QRValidationRequest(BaseModel):
    qr_data: str
    student_id: str

class AttendanceMarkRequest(BaseModel):
    class_id: int
    student_id: str
    qr_validation: str

# --- Dependencies ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Endpoints ---

# Student Login (simple authentication)
@app.post("/login/student")
def student_login(login_data: StudentLoginIn):
    db = next(get_db())
    
    # Student name mapping for demo
    name_mappings = {
        "gab": "S001",
        "prabh": "S002", 
        "S001": "S001",
        "S002": "S002"
    }
    
    # Check if input is a name that should be mapped to student ID
    student_id_to_check = name_mappings.get(login_data.student_id, login_data.student_id)
    
    # Simple validation - check if student exists
    student = db.query(Student).filter(Student.student_id == student_id_to_check).first()
    if not student:
        raise HTTPException(404, "Student not found")
    
    # Simple password check (no real auth - just accept any password for now)
    # In production, you'd verify against a hashed password
    valid_students = ["S001", "S002"]
    if student_id_to_check not in valid_students:
        raise HTTPException(400, "Invalid student ID")
    
    return {
        "status": "success", 
        "message": "Login successful",
        "student": {
            "student_id": student.student_id,
            "name": student.name,
            "interests": student.interests
        }
    }

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
    all_subjects = [row[0] for row in db.query(Score.subject).distinct()]
    
    # Subject mapping from interests to actual subjects
    interest_to_subject = {
        'ai': 'Computer Science',
        'ml': 'Computer Science', 
        'dsa': 'Computer Science',
        'math': 'Math',
        'physics': 'Physics',
        'research': 'Physics',
        'computer science': 'Computer Science',
        'english': 'English'
    }
    
    result = []
    for s in students:
        # Get scores for this student
        scores = db.query(Score).filter(Score.student_id == s.student_id).all()
        student_scores = {sc.subject: sc.marks for sc in scores}
        
        # Calculate subject priorities based on low scores (need improvement)
        subject_priorities = {}
        
        # 1. Priority based on low scores (lower score = higher priority for improvement)
        if student_scores:
            for subject in all_subjects:
                if subject in student_scores:
                    # Lower scores get higher priority (inverse relationship)
                    score = student_scores[subject]
                    # Convert score to priority (0-100 score becomes 100-0 priority)
                    priority = max(0, 100 - score) / 100.0
                    subject_priorities[subject] = priority
                else:
                    # No score available, give medium priority
                    subject_priorities[subject] = 0.5
        else:
            # No scores available, use equal priority
            for subject in all_subjects:
                subject_priorities[subject] = 0.5
        
        # 2. Boost priority based on interests
        if s.interests:
            interests_list = [i.strip().lower() for i in s.interests.split(",") if i.strip()]
            for interest in interests_list:
                mapped_subject = interest_to_subject.get(interest.lower())
                if mapped_subject and mapped_subject in subject_priorities:
                    # Boost the priority for subjects matching interests
                    subject_priorities[mapped_subject] += 0.3
        
        # Sort subjects by priority (highest first)
        sorted_subjects = sorted(subject_priorities.items(), key=lambda x: x[1], reverse=True)
        top_suggestions = [subject for subject, priority in sorted_subjects[:3]]
        
        result.append({
            "student_id": s.student_id,
            "name": s.name,
            "top_suggestions": top_suggestions
        })
    
    return {"status": "success", "students": result}

# Suggestions (student view)
@app.get("/suggestions/{student_id}")
def get_student_suggestions(student_id: str):
    db = next(get_db())
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise HTTPException(404, "Student not found")
    
    all_subjects = [row[0] for row in db.query(Score.subject).distinct()]
    
    # Subject mapping from interests to actual subjects
    interest_to_subject = {
        'ai': 'Computer Science',
        'ml': 'Computer Science', 
        'dsa': 'Computer Science',
        'math': 'Math',
        'physics': 'Physics',
        'research': 'Physics',
        'computer science': 'Computer Science',
        'english': 'English'
    }
    
    # Get scores for this student
    scores = db.query(Score).filter(Score.student_id == student_id).all()
    student_scores = {sc.subject: sc.marks for sc in scores}
    
    # Calculate subject priorities
    subject_priorities = {}
    
    # Priority based on low scores (need improvement)
    if student_scores:
        for subject in all_subjects:
            if subject in student_scores:
                score = student_scores[subject]
                # Lower scores get higher priority
                priority = max(0, 100 - score) / 100.0
                subject_priorities[subject] = priority
            else:
                subject_priorities[subject] = 0.5
    else:
        for subject in all_subjects:
            subject_priorities[subject] = 0.5
    
    # Boost priority based on interests
    if student.interests:
        interests_list = [i.strip().lower() for i in student.interests.split(",") if i.strip()]
        for interest in interests_list:
            mapped_subject = interest_to_subject.get(interest.lower())
            if mapped_subject and mapped_subject in subject_priorities:
                subject_priorities[mapped_subject] += 0.3
    
    # Sort subjects by priority
    sorted_subjects = sorted(subject_priorities.items(), key=lambda x: x[1], reverse=True)
    top_suggestions = [subject for subject, priority in sorted_subjects[:3]]
    
    return {
        "status": "success",
        "student_id": student_id,
        "top_suggestions": top_suggestions
    }

# Timetable (student)
@app.get("/timetable/s/{student_id}")
def get_student_timetable(student_id: str):
    db = next(get_db())
    # Get all timetable entries with teacher names
    timetable = db.query(Timetable, Teacher.name).join(
        Teacher, Timetable.teacher_id == Teacher.teacher_id
    ).all()
    
    result = []
    for timetable_entry, teacher_name in timetable:
        result.append({
            "timetable_id": timetable_entry.timetable_id,
            "day_of_week": timetable_entry.day_of_week,
            "subject": timetable_entry.subject,
            "teacher_id": timetable_entry.teacher_id,
            "teacher_name": teacher_name,
            "start_time": str(timetable_entry.start_time),
            "end_time": str(timetable_entry.end_time)
        })
    
    return {"status": "success", "student_id": student_id, "timetable": result}

# Timetable (teacher)
@app.get("/timetable/t/{teacher_id}")
def get_teacher_timetable(teacher_id: str):
    db = next(get_db())
    timetable = db.query(Timetable, Teacher.name).join(
        Teacher, Timetable.teacher_id == Teacher.teacher_id
    ).filter(Timetable.teacher_id == teacher_id).all()
    
    result = []
    for timetable_entry, teacher_name in timetable:
        result.append({
            "timetable_id": timetable_entry.timetable_id,
            "day_of_week": timetable_entry.day_of_week,
            "subject": timetable_entry.subject,
            "teacher_id": timetable_entry.teacher_id,
            "teacher_name": teacher_name,
            "start_time": str(timetable_entry.start_time),
            "end_time": str(timetable_entry.end_time)
        })
    
    return {"status": "success", "teacher_id": teacher_id, "timetable": result}

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
    # Join attendance with students and classes to get complete info
    records = db.query(
        Attendance, Student.name, Class.subject, Class.date, Class.start_time
    ).join(
        Student, Attendance.student_id == Student.student_id, isouter=True
    ).join(
        Class, Attendance.class_id == Class.class_id
    ).all()
    
    result = {}
    for attendance, student_name, subject, date, start_time in records:
        if attendance.student_id:  # Skip teacher attendance records (student_id = None)
            student_id = attendance.student_id
            if student_id not in result:
                result[student_id] = {  
                    "student_name": student_name or f"Student {student_id}",
                    "records": []
                }
            
            result[student_id]["records"].append({
                "attendance_id": attendance.attendance_id,
                "class_id": attendance.class_id,
                "subject": subject,
                "date": str(date),
                "time": str(start_time),
                "present": attendance.present,
                "teacher_present": attendance.teacher_present
            })
    
    return {"status": "success", "attendance": result}

# Attendance View (student)
@app.get("/getattendance/{student_id}")
def get_student_attendance(student_id: str):
    db = next(get_db())
    # Join attendance with class info
    records = db.query(
        Attendance, Class.subject, Class.date, Class.start_time
    ).join(
        Class, Attendance.class_id == Class.class_id
    ).filter(Attendance.student_id == student_id).all()
    
    result = []
    for attendance, subject, date, start_time in records:
        result.append({
            "attendance_id": attendance.attendance_id,
            "class_id": attendance.class_id,
            "subject": subject,
            "date": str(date),
            "time": str(start_time),
            "present": attendance.present
        })
    
    return {
        "status": "success",
        "student_id": student_id,
        "records": result
    }

# QR Code endpoints - temporarily disabled until packages are installed
# @app.post("/generate-qr")
# def generate_class_qr(request: QRCodeRequest):
#     """Generate QR code for a class session"""
#     # Implementation commented out - needs qrcode package
#     raise HTTPException(501, "QR code generation not implemented yet")

# @app.post("/validate-qr") 
# def validate_qr_and_mark_attendance(request: QRValidationRequest):
#     """Validate QR code and mark student attendance"""
#     # Implementation commented out - needs qrcode package  
#     raise HTTPException(501, "QR code validation not implemented yet")

# @app.get("/active-qr/{class_id}")
# def get_active_qr(class_id: int):
#     """Get active QR code for a class if it exists and is still valid"""
#     # Implementation commented out - needs qrcode package
#     raise HTTPException(501, "QR code retrieval not implemented yet")