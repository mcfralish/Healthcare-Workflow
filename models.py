import datetime
from typing_extensions import Self
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import *
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
meta = MetaData()
db = SQLAlchemy()


assigned_task_table = db.Table(
    "task",
    meta,
    db.Column("task_id", ForeignKey("Task.id"), primary_key=True),
    db.Column("patient_id", ForeignKey("Patient.id"), primary_key=True),
    db.Column("emp_id", ForeignKey("Employee.id"), primary_key=True),
)


class Users(db.Model, UserMixin, Base):
    id = db.Column(db.Integer, primary_key=True)
    employee = relationship("Employee", uselist=False)
    patient = relationship("Patient", uselist=False)


class Department(db.Model, Base):
    dept_no = db.Column(db.Integer, primary_key=True)
    dep_name = db.Column(db.String(200))
    building = db.Column(db.String(200))
    floor = db.Column(db.Integer)
    assigned_employees = relationship("Employee")
    assigned_patients = relationship("Patient")


class Shift(db.Model, Base):
    shift_id = db.Column(db.Integer, primary_key=True)
    shift_start = db.Column(db.DateTime)
    shift_end = db.Column(db.DateTime)
    work_days = db.Column(db.String(11))
    assigned_employees = relationship("Employee")


class Certification(db.Model, Base):
    cert_id = db.Column(db.Integer, primary_key=True)
    cert_name = db.Column(db.String(5))
    pay = db.Column(db.Float)
    qualified_emloyees = relationship("Employee")
    qualified_tasks = relationship("Task")


class Employee(db.Model, Base):
    empl_id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(1))
    first_name = db.Column(db.String(200))
    last_name = db.Column(db.String(200))
    phone = db.Column(db.Integer)
    dob = db.Column(db.DateTime)
    gender = db.Column(db.String(1))
    hire = db.Column(db.DateTime)
    login_id = db.Column(Integer, ForeignKey(Users.id))
    dept_no = db.Column(db.Integer, ForeignKey(Department.dept_no))
    shift_no = db.Column(db.Integer, ForeignKey(Shift.shift_id))
    cert_id = db.Column(db.Integer, ForeignKey(Certification.cert_id))


class Patient(db.Model, Base):
    patient_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(200))
    last_name = db.Column(db.String(200))
    phone = db.Column(db.Integer)
    dob = db.Column(db.DateTime)
    gender = db.Column(db.String(1))
    login_id = db.Column(Integer, ForeignKey(Users.id))
    caretaker_id = db.Column(db.Integer, ForeignKey(Employee.empl_id))
    dept_no = db.Column(db.Integer, ForeignKey(Department.dept_no))
    visitors = relationship("Guest")


class Guest(db.Model, Base):
    guest_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(200))
    last_name = db.Column(db.String(200))
    association = db.Column(db.String(200))
    visiting_pt = db.Column(db.Integer, ForeignKey(Patient.patient_id))


class Task(db.Model, Base):
    task_id = db.Column(db.Integer, primary_key=True)
    required_cert = db.Column(db.Integer, ForeignKey(Certification.cert_id))
    task_name = db.Column(db.String(200))
    priority = db.Column(db.Integer)
    duration = db.Column(db.Integer)
    required = db.Column(db.Boolean)
    recurring = db.Column(db.Boolean)
    frequency = db.Column(db.Integer)
    isMedicine = db.Column(db.Boolean)
