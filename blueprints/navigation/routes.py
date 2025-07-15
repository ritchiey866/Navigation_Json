from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, session
from services.navigation_service import NavigationService

# Create the blueprint
navigation_bp = Blueprint('navigation', __name__, url_prefix='/navigation')

@navigation_bp.route('/')
def index():
    """Display the navigation management dashboard"""
    # Check if user has admin access
    if session.get('user_role') != 'admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('index'))
    
    navigation_data = NavigationService.load_navigation()
    
    # Process navigation data for display
    navigation_items = []
    
    def process_items(items, level=0, parent=None):
        for item in items:
            # Create a copy of the item for display
            display_item = item.copy()
            display_item['level'] = level
            
            # Set parent information
            if parent:
                display_item['parent'] = parent
                display_item['parent_title'] = parent['title']
                display_item['parent_id'] = parent['id']
            else:
                display_item['parent'] = None
                display_item['parent_title'] = None
                display_item['parent_id'] = None
            
            # Check if item has children
            if 'children' in item and item['children']:
                display_item['has_children'] = True
            else:
                display_item['has_children'] = False
            
            # Add to navigation items list
            navigation_items.append(display_item)
            
            # Process children recursively
            if 'children' in item and item['children']:
                process_items(item['children'], level + 1, item)
    
    process_items(navigation_data)
    
    # Sort items by access level (admin -> developer -> user) and then by parent title
    role_order = {'admin': 0, 'developer': 1, 'user': 2}
    navigation_items.sort(key=lambda x: (
        role_order.get(x['access'], 999),  # First sort by access level
        x['parent_title'] if x['parent_title'] else 'zzz',  # Then by parent title (items without parents go last)
        x['title']  # Finally by item title
    ))
    
    return render_template('navigation/index.html', navigation_items=navigation_items)

@navigation_bp.route('/item/new', methods=['GET', 'POST'])
def new_item():
    """Create a new navigation item"""
    # Check if user has admin access
    if session.get('user_role') != 'admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        # Get form data
        title = request.form.get('title')
        access = request.form.get('access')
        page = request.form.get('page')
        parent_id = request.form.get('parent_id')
        
        # Create new item
        new_item = {
            'title': title,
            'access': access
        }
        
        if page:
            new_item['page'] = page
        
        # Create the item using the service
        NavigationService.create_item(new_item, parent_id)
        
        flash('Navigation item created successfully.', 'success')
        return redirect(url_for('navigation.index'))
    
    # GET request - display form
    # Get parent options for dropdown
    parent_options = NavigationService.get_parent_options()
    
    return render_template('navigation/new_item.html', parent_options=parent_options)

@navigation_bp.route('/item/<item_id>/edit', methods=['GET', 'POST'])
def edit_item(item_id):
    """Edit a navigation item"""
    # Check if user has admin access
    if session.get('user_role') != 'admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('index'))
    
    # Find the item to edit
    item_to_edit = NavigationService.get_item_by_id(item_id)
    parent = NavigationService.get_parent_of_item(item_id)
    
    if not item_to_edit:
        flash('Navigation item not found.', 'danger')
        return redirect(url_for('navigation.index'))
    
    if request.method == 'POST':
        # Get form data
        title = request.form.get('title')
        access = request.form.get('access')
        page = request.form.get('page')
        new_parent_id = request.form.get('parent_id')
        
        # Update item
        item_data = {
            'title': title,
            'access': access
        }
        
        if page:
            item_data['page'] = page
        
        # Update the item using the service
        NavigationService.update_item(item_id, item_data, new_parent_id)
        
        flash('Navigation item updated successfully.', 'success')
        return redirect(url_for('navigation.index'))
    
    # GET request - display form
    # Get parent options for dropdown
    parent_options = NavigationService.get_parent_options(exclude_id=item_id)
    
    # Get current parent ID
    current_parent_id = parent['id'] if parent else None
    
    return render_template('navigation/edit_item.html', 
                         item=item_to_edit, 
                         parent_options=parent_options,
                         current_parent_id=current_parent_id)

@navigation_bp.route('/item/<item_id>/delete', methods=['POST'])
def delete_item(item_id):
    """Delete a navigation item"""
    # Check if user has admin access
    if session.get('user_role') != 'admin':
        return jsonify({'success': False, 'message': 'You do not have permission to perform this action.'})
    
    # Delete the item using the service
    success = NavigationService.delete_item(item_id)
    
    if not success:
        return jsonify({'success': False, 'message': 'Navigation item not found.'})
    
    return jsonify({'success': True, 'message': 'Navigation item deleted successfully.'})

@navigation_bp.route('/reorder', methods=['POST'])
def reorder_items():
    """Reorder navigation items"""
    # Check if user has admin access
    if session.get('user_role') != 'admin':
        return jsonify({'success': False, 'message': 'You do not have permission to perform this action.'})
    
    order = request.json.get('order', [])
    
    # Reorder items using the service
    NavigationService.reorder_items(order)
    
    return jsonify({'success': True, 'message': 'Navigation items reordered successfully.'})

@navigation_bp.route('/check-leaves')
def check_leaves():
    """Check for leaf items without page links"""
    # Check if user has admin access
    if session.get('user_role') != 'admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('index'))
    
    navigation_data = NavigationService.load_navigation()
    
    # Find all leaf items
    leaf_items = []
    
    def find_leaf_items(items, parent_path=""):
        for item in items:
            current_path = f"{parent_path} > {item['title']}" if parent_path else item['title']
            
            if 'children' in item and item['children']:
                find_leaf_items(item['children'], current_path)
            else:
                leaf_items.append({
                    'id': item.get('id', ''),
                    'title': item['title'],
                    'path': current_path,
                    'has_page': 'page' in item,
                    'access': item.get('access', 'user')
                })
    
    find_leaf_items(navigation_data)
    
    # Sort by access level
    role_order = {'admin': 0, 'developer': 1, 'user': 2}
    leaf_items.sort(key=lambda x: (role_order.get(x['access'], 999), x['path']))
    
    return render_template('navigation/check_leaves.html', leaf_items=leaf_items)

@navigation_bp.route('/hierarchy')
def hierarchy():
    """Display the navigation hierarchy"""
    # Check if user has admin access
    if session.get('user_role') != 'admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('index'))
    
    navigation_data = NavigationService.load_navigation()
    
    # Process navigation data for display
    navigation_items = []
    
    def process_items(items, level=0, parent=None):
        for item in items:
            # Create a copy of the item for display
            display_item = item.copy()
            display_item['level'] = level
            
            # Set parent information
            if parent:
                display_item['parent'] = parent
                display_item['parent_title'] = parent['title']
                display_item['parent_id'] = parent['id']
            else:
                display_item['parent'] = None
                display_item['parent_title'] = None
                display_item['parent_id'] = None
            
            # Check if item has children
            if 'children' in item and item['children']:
                display_item['has_children'] = True
                # Process children recursively
                process_items(item['children'], level + 1, item)
            else:
                display_item['has_children'] = False
            
            # Add to navigation items list
            navigation_items.append(display_item)
    
    process_items(navigation_data)
    
    # Sort items by access level (admin -> developer -> user) and then by parent title
    role_order = {'admin': 0, 'developer': 1, 'user': 2}
    navigation_items.sort(key=lambda x: (
        role_order.get(x['access'], 999),  # First sort by access level
        x['parent_title'] if x['parent_title'] else 'zzz',  # Then by parent title (items without parents go last)
        x['title']  # Finally by item title
    ))
    
    return render_template('navigation/hierarchy.html', navigation_items=navigation_items) 