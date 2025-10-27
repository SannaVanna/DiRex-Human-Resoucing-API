from flask import Blueprint, request, session, jsonify
from src.models import Employee
from src.flasklogin import login_manager
from src.db import db

post_employee_bp = Blueprint('post_employee_bp', __name__)  

#========================================
#POST EMPLOYEE
#========================================

@post_employee_bp.route('/employees', methods=['POST'])
def add_employee():
    data = request.get_json()
    # Basic validation
    if not all(k in data for k in ('name', 'email', 'position', 'salary')):
        return jsonify({'message': 'Missing fields'}), 400

    # Optional: ensure unique email
    if Employee.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Employee with this email already exists'}), 400

    new_emp = Employee(
        name=data['name'],
        email=data['email'],
        position=data['position'],
        salary=data['salary']
    )
    db.session.add(new_emp)
    db.session.commit()
    return jsonify({'message': 'Employee added successfully', 'employee': new_emp.to_dict()}), 201
