from flask import Blueprint, request, session, jsonify, abort, g
from src.models import Employee
from src.flasklogin import login_manager
from src.db import db

put_employee_bp = Blueprint('put_employee_bp', __name__)

#========================================
#PUT EMPLOYEE
#========================================


@put_employee_bp.route('/employees/<int:id>', methods=['PUT'])
def update_employee(id):
    emp = Employee.query.get(id)
    if not emp:
        return jsonify({'message': 'Employee not found'}), 404

    data = request.get_json()
    emp.name = data.get('name', emp.name)
    emp.email = data.get('email', emp.email)
    emp.position = data.get('position', emp.position)
    emp.salary = data.get('salary', emp.salary)

    db.session.commit()
    return jsonify({'message': 'Employee updated successfully', 'employee': emp.to_dict()}), 200
