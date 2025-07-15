from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
import json
import os
from werkzeug.security import generate_password_hash, check_password_hash

bp = Blueprint('page2', __name__, url_prefix='/page2')

# Path to the users JSON file
USERS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'users.json')

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_users(users):
    os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)

@bp.route('/')
def index():
    users = load_users()
    return render_template('page2.html', users=users)

@bp.route('/user/new')
def new_user():
    return render_template('page2/user_form.html')

@bp.route('/user/<int:user_id>/edit')
def edit_user(user_id):
    users = load_users()
    user = next((user for user in users if user['id'] == user_id), None)
    if user is None:
        flash('User not found', 'error')
        return redirect(url_for('page2.index'))
    return render_template('page2/user_form.html', user=user)

@bp.route('/user/save', methods=['POST'])
@bp.route('/user/<int:user_id>/save', methods=['POST'])
def save_user(user_id=None):
    users = load_users()
    
    # Get form data
    name = request.form.get('name')
    email = request.form.get('email')
    role = request.form.get('role')
    status = request.form.get('status')
    password = request.form.get('password')
    
    if user_id is None:
        # Create new user
        new_id = max([user['id'] for user in users], default=0) + 1
        user = {
            'id': new_id,
            'name': name,
            'email': email,
            'role': role,
            'status': status,
            'password': generate_password_hash(password) if password else None
        }
        users.append(user)
        flash('User created successfully', 'success')
    else:
        # Update existing user
        user = next((user for user in users if user['id'] == user_id), None)
        if user is None:
            flash('User not found', 'error')
            return redirect(url_for('page2.index'))
        
        user.update({
            'name': name,
            'email': email,
            'role': role,
            'status': status
        })
        
        if password:
            user['password'] = generate_password_hash(password)
        
        flash('User updated successfully', 'success')
    
    save_users(users)
    return redirect(url_for('page2.index'))

@bp.route('/user/<int:user_id>/delete', methods=['POST'])
def delete_user(user_id):
    users = load_users()
    user = next((user for user in users if user['id'] == user_id), None)
    
    if user is None:
        return jsonify({'success': False, 'message': 'User not found'})
    
    users = [user for user in users if user['id'] != user_id]
    save_users(users)
    
    return jsonify({'success': True, 'message': 'User deleted successfully'}) 