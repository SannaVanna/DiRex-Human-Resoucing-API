from flask import Blueprint, request, session, jsonify, abort, g
from src.models import Admin, Employee
from src.flasklogin import login_manager
from src.db import db
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth_bp', __name__)


#========================================
#AUTHENTICATION ROUTES
#========================================
@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if Admin.query.filter_by(username=username).first():
        return jsonify({'message': 'Admin already exists'}), 400

    hashed_pw = generate_password_hash(password)
    admin = Admin(username=username, password=hashed_pw)
    db.session.add(admin)
    db.session.commit()
    return jsonify({'message': 'Admin account created successfully'}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    admin = Admin.query.filter_by(username=username).first()
    if not admin or not check_password_hash(admin.password, password):
        return jsonify({'message': 'Invalid username or password'}), 401

    return jsonify({'message': 'Login successful', 'admin': admin.username}), 200