from flask import Blueprint, render_template, flash, request, redirect, url_for, session, jsonify, abort, g
from src.models import Admin, Employee
from .flasklogin import login_manager
from src.db import db
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
#from flask.view import MethodView


routes = Blueprint('routes', __name__)


@login_manager.user_loader
def load_user(admin_id):
    return Admin.query.get(int(admin_id))


@routes.before_request
def set_current_user():
    g.user = current_user


def admin_required_api(f)    :
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('admin_id'):
            admin = Admin.query.get(session['admin_id'])
            if admin:
                request.admin = admin
                return f(*args, **kwargs)
        auth = request.headers.get('Authorization')
        if auth:
            parts = auth.split()    
            if len(parts) == 2 and parts[0].lower() == 'bearer':
                token = parts[1]
                admin = Admin.verify_token(token)
                if admin:
                    request.admin = admin 
                    return f(*args, **kwargs)
        return jsonify({"errors": "admin authentication required"})        
    return decorated
    
def admin_session_required(f):
    @wraps(f)    
    def decorated(*args, **kwargs):
        if not session.get('admin_id'):
            return redirect(url_for('routes.login'))
        return f(*args, **kwargs)
    return decorated


@routes.route("/", methods=["GET", "POST"])
@routes.route('/index')
def docs():
    return render_template("index.html")


# ---------- AUTH ----------
@routes.route('/signup', methods=['GET', 'POST'])
def register():
    print("SIGNUP ROUTE TRIGGERED")
    if request.method == 'POST':
        first_name = request.form['first_name'].strip()
        last_name = request.form['last_name'].strip()
        email = request.form['email'].strip().lower()
        password = request.form['password']

        if Admin.query.filter_by(email=email).first():
            flash("Email already registered", "warning")
            return render_template('signup.html')
        
        admin = Admin(
            first_name=first_name,      
            last_name=last_name,
            email=email,
            password=password,
            created_at=None
        )
        db.session.add(admin)
        db.session.commit()
        flash("Registration successful. Please log in.", "success")
        return redirect(url_for('routes.login'))
    return render_template('signup.html')


@routes.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        admin = Admin.query.filter_by(email=email).first()
        if admin and check_password_hash(admin.password, password):
            session["admin_id"] = admin.id
            return redirect(url_for("routes.dashboard"))
        else:
            return render_template("login.html", error="Invalid login credentials")
    return render_template("login.html")


@routes.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("routes.login"))


# ---------- ADMIN DASHBOARD ----------
@routes.route("/dashboard")
def dashboard():
    admin_id = session.get('admin_id')
    if "admin_id" not in session:
        return redirect(url_for("routes.login"))
    admin = Admin.query.get(admin_id)
    return render_template("admin_dashboard.html", admin=admin)


# ---------- UI ENDPOINTS ----------
@routes.route("/employees/add", methods=["GET", "POST"])
def add_employee_ui():
    if "admin_id" not in session:
        return redirect(url_for("routes.login"))

    if request.method == "POST":
        emp = Employee(
            employee_id=request.form["employee_id"],
            first_name=request.form["first_name"],
            last_name=request.form["last_name"],
            email=request.form["email"],
            department=request.form.get("department"),
            position=request.form.get("position"),
            salary=request.form.get("salary"),
            remark=request.form.get("remark"),
        )
        db.session.add(emp)
        db.session.commit()
        return redirect(url_for("routes.dashboard"))
    return render_template("add_employee.html")


@routes.route("/employees/view")
def view_employees_ui():
    admin_id = session.get('admin_id')
    if "admin_id" not in session:
        return redirect(url_for("routes.login"))
    admin = Admin.query.get(admin_id)

    search = request.args.get("search", "")
    if search:
        employees = Employee.query.filter(
            (Employee.first_name.ilike(f"%{search}%")) |
            (Employee.last_name.ilike(f"%{search}%")) |
            (Employee.employee_id.ilike(f"%{search}%"))
        ).all()
    else:
        employees = Employee.query.all()
    return render_template("view_employees.html", employees=employees, search=search, admin=admin)


@routes.route("/employees/<emp_id>")
def employee_details_ui(emp_id):
    emp = Employee.query.filter_by(employee_id=emp_id).first_or_404()
    return render_template("employee_details.html", emp=emp)


@routes.route("/employees/update/<emp_id>", methods=["GET", "POST"])
def update_employee_ui(emp_id):
    emp = Employee.query.filter_by(employee_id=emp_id).first_or_404()
    if request.method == "POST":
        emp.first_name = request.form["first_name"]
        emp.last_name = request.form["last_name"]
        emp.email = request.form["email"]
        emp.department = request.form["department"]
        emp.position = request.form["position"]
        emp.salary = request.form["salary"]
        emp.remark = request.form["remark"]
        db.session.commit()
        return redirect(url_for("routes.view_employees_ui"))
    return render_template("update_employee.html", emp=emp)


@routes.route("/employees/delete/<emp_id>", methods=["GET", "POST"])
def delete_employee_ui(emp_id):
    emp = Employee.query.filter_by(employee_id=emp_id).first_or_404()
    if request.method == "POST":
        db.session.delete(emp)
        db.session.commit()
        return redirect(url_for("routes.view_employees_ui"))
    return render_template("delete_confirm.html", emp=emp)


# ---------- API ENDPOINTS (JSON) ----------
@routes.route("/api/employees", methods=["GET"])
def get_employees():
    employees = Employee.query.all()
    return jsonify([{
        "employee_id": e.employee_id,
        "first_name": e.first_name,
        "last_name": e.last_name,
        "email": e.email,
        "department": e.department,
        "position": e.position,
        "salary": e.salary,
        "remark": e.remark
    } for e in employees])


@routes.route("/api/employees/<emp_id>", methods=["GET"])
def get_employee(emp_id):
    emp = Employee.query.filter_by(employee_id=emp_id).first_or_404()
    return jsonify({
        "employee_id": emp.employee_id,
        "first_name": emp.first_name,
        "last_name": emp.last_name,
        "email": emp.email,
        "department": emp.department,
        "position": emp.position,
        "salary": emp.salary,
        "remark": emp.remark
    })


@routes.route("/api/employees", methods=["POST"])
def add_employee_api():
    data = request.get_json()
    emp = Employee(**data)
    db.session.add(emp)
    db.session.commit()
    return jsonify({"message": "Employee added successfully"}), 201


@routes.route("/api/employees/<emp_id>", methods=["PUT"])
def update_employee_api(emp_id):
    emp = Employee.query.filter_by(employee_id=emp_id).first_or_404()
    data = request.get_json()
    for key, value in data.items():
        setattr(emp, key, value)
    db.session.commit()
    return jsonify({"message": "Employee updated successfully"})


@routes.route("/api/employees/<emp_id>", methods=["DELETE"])
def delete_employee_api(emp_id):
    emp = Employee.query.filter_by(employee_id=emp_id).first_or_404()
    db.session.delete(emp)
    db.session.commit()
    return jsonify({"message": "Employee deleted successfully"})

