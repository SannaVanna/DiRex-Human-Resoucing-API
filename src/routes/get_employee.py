from flask import Blueprint, render_template, flash, request, redirect, url_for, session, jsonify, abort, g
from src.models import Admin, Employee
from src.flasklogin import login_manager
from src.db import db
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

get_employee_bp = Blueprint('get_employee_bp', __name__)

#========================================
#GET EMPLOYEE(S)
#========================================

@get_employee_bp.route('/employees', methods=['GET'])
def get_employees():
    employees = Employee.query.all()
    output = [emp.to_dict() for emp in employees]
    return jsonify({'employees': output}), 200


@get_employee_bp.route('/employees/<int:id>', methods=['GET'])
def get_employee(id):
    emp = Employee.query.get(id)
    if not emp:
        return jsonify({'message': 'Employee not found'}), 404
    return jsonify({'employee': emp.to_dict()}), 200

