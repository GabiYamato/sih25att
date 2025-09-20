import random
from datetime import date, time, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import Base, Student, Teacher, Timetable, Class, Attendance, Score  # import models from your main API file
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- DB Setup ---
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# --- Create Tables ---
Base.metadata.create_all(bind=engine)

def prefill_data():
    db = SessionLocal()

    # Clear existing data (so script can be rerun)
    db.query(Attendance).delete()
    db.query(Score).delete()
    db.query(Class).delete()
    db.query(Timetable).delete()
    db.query(Student).delete()
    db.query(Teacher).delete()
    db.commit()

    # --- Students ---
    students = [
        Student(student_id="S001", name="Ryan", interests="AI,Math,DSA"),
        Student(student_id="S002", name="Alex", interests="Physics,ML,Research")
    ]
    db.add_all(students)

    # --- Teachers ---
    teachers = [
        Teacher(teacher_id="T001", name="Dr. Smith", subject="Math"),
        Teacher(teacher_id="T002", name="Dr. Brown", subject="Physics"),
        Teacher(teacher_id="T003", name="Dr. Taylor", subject="Computer Science"),
        Teacher(teacher_id="T004", name="Dr. Green", subject="English")
    ]
    db.add_all(teachers)

    # --- Timetable (Mon–Thu, one subject per day) ---
    timetable_entries = [
        Timetable(day_of_week="Mon", subject="Math", teacher_id="T001",
                  start_time=time(9, 0), end_time=time(10, 0)),
        Timetable(day_of_week="Tue", subject="Physics", teacher_id="T002",
                  start_time=time(10, 0), end_time=time(11, 0)),
        Timetable(day_of_week="Wed", subject="Computer Science", teacher_id="T003",
                  start_time=time(11, 0), end_time=time(12, 0)),
        Timetable(day_of_week="Thu", subject="English", teacher_id="T004",
                  start_time=time(9, 0), end_time=time(10, 0))
    ]
    db.add_all(timetable_entries)
    db.commit()

    # --- Generate 1 week of classes (Mon–Fri) ---
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())  # Monday this week

    subjects = [
        ("Math", "T001", time(9, 0), time(10, 0)),
        ("Physics", "T002", time(10, 0), time(11, 0)),
        ("Computer Science", "T003", time(11, 0), time(12, 0)),
        ("English", "T004", time(9, 0), time(10, 0))
    ]

    all_classes = []
    for i in range(5):  # Mon–Fri
        day = start_of_week + timedelta(days=i)
        subject, teacher_id, st, et = subjects[i % len(subjects)]  # rotate subjects
        cls = Class(
            subject=subject,
            teacher_id=teacher_id,
            date=day,
            start_time=st,
            end_time=et,
            qr_code=str(random.randint(10000, 99999)),
            status="completed"
        )
        db.add(cls)
        db.commit()
        all_classes.append(cls)

        # Teacher attendance (always present)
        db.add(Attendance(class_id=cls.class_id, teacher_present=True))

        # Student attendance (random present/absent)
        for sid in ["S001", "S002"]:
            db.add(Attendance(class_id=cls.class_id, student_id=sid,
                              present=random.choice([True, False])))

    # --- Scores ---
    scores = [
        Score(student_id="S001", subject="Math", marks=85),
        Score(student_id="S001", subject="Physics", marks=78),
        Score(student_id="S001", subject="Computer Science", marks=92),
        Score(student_id="S002", subject="Math", marks=90),
        Score(student_id="S002", subject="English", marks=88),
        Score(student_id="S002", subject="Physics", marks=82)
    ]
    db.add_all(scores)

    db.commit()
    db.close()
    print("✅ Prefill complete: students, teachers, timetable, 1 week of classes, random attendance & scores added.")

if __name__ == "__main__":
    prefill_data()
