from flask import Blueprint, request, jsonify, session
from services.navigation_service import NavigationService

# Create the blueprint
navigation_api_bp = Blueprint('navigation_api', __name__, url_prefix='/api/navigation')

@navigation_api_bp.route('/items', methods=['GET'])
def get_items():
    """Get all navigation items"""
    # Check if user has admin access
    if session.get('user_role') != 'admin':
        return jsonify({'success': False, 'message': 'You do not have permission to perform this action.'}), 403
    
    items = NavigationService.get_all_items()
    return jsonify({'success': True, 'items': items})

@navigation_api_bp.route('/items/<item_id>', methods=['GET'])
def get_item(item_id):
    """Get a navigation item by ID"""
    # Check if user has admin access
    if session.get('user_role') != 'admin':
        return jsonify({'success': False, 'message': 'You do not have permission to perform this action.'}), 403
    
    item = NavigationService.get_item_by_id(item_id)
    
    if not item:
        return jsonify({'success': False, 'message': 'Navigation item not found.'}), 404
    
    return jsonify({'success': True, 'item': item})

@navigation_api_bp.route('/items', methods=['POST'])
def create_item():
    """Create a new navigation item"""
    # Check if user has admin access
    if session.get('user_role') != 'admin':
        return jsonify({'success': False, 'message': 'You do not have permission to perform this action.'}), 403
    
    data = request.json
    
    if not data or 'title' not in data:
        return jsonify({'success': False, 'message': 'Title is required.'}), 400
    
    parent_id = data.get('parent_id')
    
    new_item = NavigationService.create_item(data, parent_id)
    
    return jsonify({'success': True, 'item': new_item, 'message': 'Navigation item created successfully.'})

@navigation_api_bp.route('/items/<item_id>', methods=['PUT'])
def update_item(item_id):
    """Update a navigation item"""
    # Check if user has admin access
    if session.get('user_role') != 'admin':
        return jsonify({'success': False, 'message': 'You do not have permission to perform this action.'}), 403
    
    data = request.json
    
    if not data:
        return jsonify({'success': False, 'message': 'No data provided.'}), 400
    
    new_parent_id = data.get('parent_id')
    
    updated_item = NavigationService.update_item(item_id, data, new_parent_id)
    
    if not updated_item:
        return jsonify({'success': False, 'message': 'Navigation item not found.'}), 404
    
    return jsonify({'success': True, 'item': updated_item, 'message': 'Navigation item updated successfully.'})

@navigation_api_bp.route('/items/<item_id>', methods=['DELETE'])
def delete_item(item_id):
    """Delete a navigation item"""
    # Check if user has admin access
    if session.get('user_role') != 'admin':
        return jsonify({'success': False, 'message': 'You do not have permission to perform this action.'}), 403
    
    success = NavigationService.delete_item(item_id)
    
    if not success:
        return jsonify({'success': False, 'message': 'Navigation item not found.'}), 404
    
    return jsonify({'success': True, 'message': 'Navigation item deleted successfully.'})

@navigation_api_bp.route('/reorder', methods=['POST'])
def reorder_items():
    """Reorder navigation items"""
    # Check if user has admin access
    if session.get('user_role') != 'admin':
        return jsonify({'success': False, 'message': 'You do not have permission to perform this action.'}), 403
    
    data = request.json
    
    if not data or 'order' not in data:
        return jsonify({'success': False, 'message': 'Order is required.'}), 400
    
    order = data.get('order', [])
    
    success = NavigationService.reorder_items(order)
    
    return jsonify({'success': True, 'message': 'Navigation items reordered successfully.'})

@navigation_api_bp.route('/parent-options', methods=['GET'])
def get_parent_options():
    """Get parent options for dropdown"""
    # Check if user has admin access
    if session.get('user_role') != 'admin':
        return jsonify({'success': False, 'message': 'You do not have permission to perform this action.'}), 403
    
    exclude_id = request.args.get('exclude_id')
    
    parent_options = NavigationService.get_parent_options(exclude_id)
    
    return jsonify({'success': True, 'parent_options': parent_options}) 