import os
from flask import Flask, flash, render_template, redirect, request, url_for
from flask_login import (
    current_user,
    LoginManager,
    login_required,
    login_user,
)
from dotenv import load_dotenv, find_dotenv
from sqlalchemy import and_
from models import (
    Users,
    db,
    Department,
    Shift,
    Certification,
    Employee,
    Patient,
    Visitor,
    Task,
    AssignedTask,
)


load_dotenv(find_dotenv())
app = Flask(__name__)
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("NEW_DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
login_manager = LoginManager()
login_manager.init_app(app)


db.init_app(app)
with app.app_context():
    db.create_all()


@login_manager.user_loader
def load_user(user_id):
    """loads  current user"""
    return Users.query.get(int(user_id))


@app.route("/", methods=["GET", "POST"])
def index():
    """Renders index page"""
    if request.method == "POST":

        if request.form.get("user") == "administration":
            return render_template("a_login.html")

        if request.form.get("user") == "management":
            return render_template("m_login.html", depts=Department.query.all())

        if request.form.get("user") == "patient":
            return render_template("p_login.html")

    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Renders login page"""
    if request.method == "POST":

        if request.form.get("admin"):

            id_no = int(request.form.get("admin"))
            emp = Employee.query.filter_by(empl_no=id_no).first()
            if emp and emp.status == "A":
                user = Users.query.filter_by(id=emp.login_id).first()
                login_user(user)
                return redirect(url_for("admin"))

            flash("That Employee Number is not associated with an admin account.")
            return render_template("index.html")

        if request.form.get("management"):

            id_no = int(request.form.get("management"))
            emp = Employee.query.filter_by(empl_no=id_no).first()
            emps = Employee.query.all()
            if emp and (emp.status == "A" or emp.status == "M"):
                user = Users.query.filter_by(id=emp.login_id).first()
                login_user(user)
                return redirect(url_for("manager"))

            flash("That Employee Number is not associated with an management account.")
            return render_template("index.html")

        if request.form.get("patient"):

            id_no = int(request.form.get("patient"))
            patient = Patient.query.filter_by(patient_no=id_no).first()
            if patient:
                user = Users.query.filter_by(id=patient.login_id).first()
                login_user(user)
                return redirect(url_for("patient"))

            flash("That Patient Number cannot be found.")
            return render_template("index.html")

    return redirect(url_for("index"))


@login_required
@app.route("/admin", methods=["GET", "POST"])
def admin():
    """Recieve input from admin to display appropriate form"""
    if request.method == "POST":
        if request.form.get("department"):
            return render_template("dept_form.html")

        if request.form.get("shift"):
            return render_template("shift_form.html")

        if request.form.get("certification"):
            return render_template("cert_form.html")

        if request.form.get("employee"):
            depts = Department.query.all()
            shifts = Shift.query.all()
            certs = Certification.query.all()
            return render_template(
                "empl_form.html", depts=depts, shifts=shifts, certs=certs
            )

        if request.form.get("patient"):
            depts = Department.query.all()
            emps = Employee.query.all()
            certs = Certification.query.all()
            return render_template(
                "patient_form.html",
                depts=depts,
                emps=emps,
                certs=certs,
            )

        if request.form.get("visitor"):
            pts = Patient.query.all()
            return render_template("visitor_form.html", pts=pts)

        if request.form.get("task"):
            certs = Certification.query.all()
            return render_template("task_form.html", certs=certs)

    return render_template("admin.html")


@login_required
@app.route("/handle_admin", methods=["POST"])
def handle_admin():
    data = request.form
    keys = data.keys()
    print(data)

    if data["type"] == "department":
        if data["dept_name"] != "":
            new = Department(
                dept_name=data["dept_name"],
                building=data["building"],
                floor=int(data["floor"]),
            )
            flash("Department Added")
        else:
            new = None
            flash("Department must have a name.")

    if data["type"] == "shift":
        work_days = ""
        if "Sunday" in keys:
            work_days += "Su "
        if "Monday" in keys:
            work_days += "M "
        if "Tuesday" in keys:
            work_days += "Tu "
        if "Wednesday" in keys:
            work_days += "W "
        if "Thursday" in keys:
            work_days += "Th "
        if "Friday" in keys:
            work_days += "F "
        if "Saturday" in keys:
            work_days += "Sa"

        if work_days != "":
            new = Shift(
                work_days=work_days,
                work_hours=data["work_hours"],
            )
            flash("Shift Added")
        else:
            new = None
            flash("Shift must include at least one day.")

    if data["type"] == "certification":
        if data["cert_name"] != "":
            new = Certification(
                cert_name=data["cert_name"],
                pay=data["pay"],
                clearance=data["clearance"],
            )
            flash("Certification Added")
        else:
            new = None
            flash("Certification must have a name.")

    if data["type"] == "employee":

        if data["first_name"] == "":
            new = None
            flash("Employee must have a first name")

        elif data["first_name"] == "":
            new = None
            flash("Employee must have a last name")

        elif data["phone"] == "":
            new = None
            flash("Employee must have a phone number")

        else:
            if data["shift_no"]:
                shift_no = int(data["shift_no"])
            else:
                shift_no = None

            new_user = Users()
            db.session.add(new_user)
            db.session.commit()
            new = Employee(
                status=data["status"],
                first_name=data["first_name"],
                last_name=data["last_name"],
                phone=str(data["phone"]),
                dob=str(data["dob"]),
                gender=data["gender"],
                hire=str(data["hire"]),
                login_id=new_user.id,
                dept_no=int(data["dept_no"]),
                shift_no=shift_no,
                cert_no=int(data["cert_no"]),
            )
            flash("Employee Added")

    if data["type"] == "patient":
        if data["first_name"] == "":
            new = None
            flash("Employee must have a first name")

        elif data["first_name"] == "":
            new = None
            flash("Employee must have a last name")

        elif data["phone"] == "":
            new = None
            flash("Employee must have a phone number")

        else:
            new_user = Users()
            db.session.add(new_user)
            db.session.commit()
            new = Patient(
                first_name=data["first_name"],
                last_name=data["last_name"],
                phone=str(data["phone"]),
                dob=str(data["dob"]),
                gender=data["gender"],
                admission_date=str(data["adm"]),
                login_id=new_user.id,
                dept_no=int(data["dept_no"]),
            )
            flash("Patient Added")

    if data["type"] == "visitor":
        if data["first_name"] == "":
            new = None
            flash("Visitor must have a first name")

        if data["last_name"] == "":
            new = None
            flash("Visitor must have a first name")

        if data["association"] == "":
            new = None
            flash("Visitor must have an association")

        else:
            new = Visitor(
                first_name=data["first_name"],
                last_name=data["last_name"],
                association=data["association"],
                visiting_pt=int(data["visiting_pt"]),
            )
            flash("Visitor Added")

    if data["type"] == "task":
        new = Task(
            task_name=data["task_name"],
            priority=int(data["priority"]),
            duration=int(data["duration"]),
            required=False,
            isMedicine=False,
            clearance=data["clearance"],
            recurring=False,
        )

        if data["required"] == "True":
            new.required = True

        if data["isMedicine"] == "True":
            new.isMedicine = True

        if data["recurring"] == "True":
            new.recurring = True

        if data["frequency"] != "":
            new.frequency = int(data["frequency"])

        if (new.recurring == False) and (new.frequency != None):
            new = None
            flash("May not include frequency on non-recurring tasks.")

        if (new.recurring == True) and (new.frequency == None):
            new = None
            flash("Must include frequency on recurring tasks.")

        else:
            flash("Task Added")

    if new:
        db.session.add(new)
        db.session.commit()

    return redirect(url_for("admin"))


@login_required
@app.route("/manager", methods=["GET", "POST"])
def manager():

    manager = Employee.query.filter_by(login_id=current_user.id).first()
    dep = Department.query.filter_by(dept_no=manager.dept_no).first()
    certs = Certification.query.all()
    tasks = Task.query.all()
    dep_pts = Patient.query.filter_by(dept_no=dep.dept_no).all()
    dep_emps = Employee.query.filter_by(dept_no=dep.dept_no).all()

    if request.method == "POST":
        data = request.form
        cleared = False
        redundant = True
        if data["action"] == "assign_task":
            assign = AssignedTask(
                requesting_pt=data["pt_no"],
                task_no=data["task_no"],
                assigned_caregiver=data["emp_no"],
            )

            caregiver_clearance = (
                Certification.query.filter_by(
                    cert_no=Employee.query.filter_by(empl_no=assign.assigned_caregiver)
                    .first()
                    .cert_no
                )
                .first()
                .clearance
            )

            required_clearance = (
                Task.query.filter_by(task_no=assign.task_no).first().clearance
            )

            if caregiver_clearance <= required_clearance:
                cleared = True
            else:
                flash("Caregiver does not meet required clearance.")

            dupes = AssignedTask.query.filter_by(
                requesting_pt=assign.requesting_pt
            ).all()

            if dupes and len(dupes) > 0:
                temp = []
                for dupe in dupes:
                    if dupe.task_no == int(assign.task_no):
                        temp.append(dupe)
                dupes = temp

            task_request = None
            if dupes and len(dupes) > 0:
                temp = []
                for dupe in dupes:
                    if dupe.assigned_caregiver != None:
                        temp.append(dupe)
                    else:
                        task_request = dupe
                dupes = temp

            update_only = False
            if task_request:
                update_only = True
                task_request.assigned_caregiver = assign.assigned_caregiver
                assign = task_request

            if dupes and len(dupes) > 0:
                flash("Someone is already working on that.")
            else:
                redundant = False

            if cleared and update_only:
                db.session.merge(assign)
                db.session.commit()
                flash("Task Assigned")

            elif cleared and not redundant:
                db.session.add(assign)
                db.session.commit()
                flash("Task Assigned")

        if data["action"] == "task_complete":
            completed = AssignedTask.query.filter_by(at_no=data["at_no"]).first()
            db.session.delete(completed)
            db.session.commit()
            flash("Task Completed")

    unassigned_tasks = AssignedTask.query.filter_by(assigned_caregiver=None).all()
    all_tasks = AssignedTask.query.all()
    assigned_tasks = []
    for task in all_tasks:
        if task.assigned_caregiver != None:
            assigned_tasks.append(task)

    unassigned_tasks.sort(
        key=lambda x: Task.query.filter_by(task_no=x.task_no).first().priority
    )
    assigned_tasks.sort(
        key=lambda x: Task.query.filter_by(task_no=x.task_no).first().priority
    )

    unassigned_list = []
    assigned_list = []

    for task in unassigned_tasks:
        task_tuple = (
            Task.query.filter_by(task_no=task.task_no).first(),
            Patient.query.filter_by(patient_no=task.requesting_pt).first(),
            task.at_no,
        )

        if task_tuple[1].dept_no == dep.dept_no:
            unassigned_list.append(task_tuple)

    for task in assigned_tasks:
        task_tuple = (
            Task.query.filter_by(task_no=task.task_no).first(),
            Patient.query.filter_by(patient_no=task.requesting_pt).first(),
            Employee.query.filter_by(empl_no=task.assigned_caregiver).first(),
            task.at_no,
        )

        if task_tuple[1].dept_no == dep.dept_no:
            assigned_list.append(task_tuple)

    return render_template(
        "management.html",
        manager=manager,
        dep=dep,
        dep_pts=dep_pts,
        dep_emps=dep_emps,
        certs=certs,
        tasks=tasks,
        unassigned_list=unassigned_list,
        assigned_list=assigned_list,
    )


@login_required
@app.route("/patient", methods=["GET", "POST"])
def patient():

    pt = Patient.query.filter_by(login_id=current_user.id).first()
    dep = Department.query.filter_by(dept_no=pt.dept_no).first()
    certs = Certification.query.all()
    requestable_tasks = Task.query.filter_by(required=False).all()

    if request.method == "POST":
        data = request.form
        new_request = AssignedTask(requesting_pt=pt.patient_no, task_no=data["task_no"])

        dupes = AssignedTask.query.filter_by(requesting_pt=pt.patient_no).all()
        if dupes and len(dupes) > 0:
            temp = []
            for dupe in dupes:
                if dupe.task_no == int(new_request.task_no):
                    temp.append(dupe)
            dupes = temp

        if dupes and len(dupes) > 0:
            flash("You may only request a task once.")
        else:
            db.session.add(new_request)
            db.session.commit()

    my_tasks = AssignedTask.query.filter_by(requesting_pt=pt.patient_no).all()
    requested = []
    assigned = []
    for task in my_tasks:
        if task.assigned_caregiver == None:
            requested.append(Task.query.filter_by(task_no=task.task_no).first())
        else:
            task_tuple = (
                Task.query.filter_by(task_no=task.task_no).first(),
                Employee.query.filter_by(empl_no=task.assigned_caregiver).first(),
            )
            assigned.append(task_tuple)

    visitors = Visitor.query.filter_by(visiting_pt=pt.patient_no).all()

    return render_template(
        "patient.html",
        certs=certs,
        pt=pt,
        dep=dep,
        requestable_tasks=requestable_tasks,
        requested=requested,
        assigned=assigned,
        visitors=visitors,
    )


if __name__ == "__main__":
    app.run(
        host=os.getenv("IP", "0.0.0.0"), port=int(os.getenv("PORT", 8080)), debug=True
    )
