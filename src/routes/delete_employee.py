from flask import Blueprint, jsonify
from src.models import Employee
from src.db import db

delete_employee_bp = Blueprint('delete_employee_bp', __name__)  

#========================================
#DELETE EMPLOYEE
#========================================

@delete_employee_bp.route('/employees/<int:id>', methods=['DELETE'])
def delete_employee(id):
    emp = Employee.query.get(id)
    if not emp:
        return jsonify({'message': 'Employee not found'}), 404

    db.session.delete(emp)
    db.session.commit()
    return jsonify({'message': 'Employee deleted successfully'}), 200
