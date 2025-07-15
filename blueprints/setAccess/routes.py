from flask import Blueprint, render_template, request, session, redirect, url_for

# Create the blueprint
setAccess_bp = Blueprint('setAccess', __name__, url_prefix='/userRole')

@setAccess_bp.route('/', methods=['GET', 'POST'])
def set_user_access():
    if request.method == 'POST':
        role = request.form.get('role')
        if role in ['user', 'admin', 'developer']:
            session['user_role'] = role
        return redirect(url_for('index'))
    return render_template('set_access.html') 