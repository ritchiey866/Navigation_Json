import json
import os
import uuid
from flask import current_app

class NavigationService:
    """Service for managing navigation data with CRUD operations"""
    
    @staticmethod
    def get_navigation_file_path():
        """Get the path to the navigation.json file"""
        return os.path.join(current_app.template_folder, 'navigation.json')
    
    @staticmethod
    def load_navigation():
        """Load the navigation data from the JSON file"""
        json_path = NavigationService.get_navigation_file_path()
        try:
            with open(json_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    @staticmethod
    def save_navigation(data):
        """Save the navigation data to the JSON file"""
        json_path = NavigationService.get_navigation_file_path()
        with open(json_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    @staticmethod
    def get_all_items():
        """Get all navigation items"""
        return NavigationService.load_navigation()
    
    @staticmethod
    def get_item_by_id(item_id):
        """Get a navigation item by ID"""
        navigation_data = NavigationService.load_navigation()
        
        def find_item(items, target_id):
            for item in items:
                if 'id' in item and item['id'] == target_id:
                    return item
                if 'children' in item and item['children']:
                    result = find_item(item['children'], target_id)
                    if result:
                        return result
            return None
        
        return find_item(navigation_data, item_id)
    
    @staticmethod
    def get_parent_of_item(item_id):
        """Get the parent of a navigation item by ID"""
        navigation_data = NavigationService.load_navigation()
        
        def find_parent(items, target_id, parent=None):
            for item in items:
                if 'id' in item and item['id'] == target_id:
                    return parent
                if 'children' in item and item['children']:
                    result = find_parent(item['children'], target_id, item)
                    if result:
                        return result
            return None
        
        return find_parent(navigation_data, item_id)
    
    @staticmethod
    def create_item(item_data, parent_id=None):
        """Create a new navigation item"""
        navigation_data = NavigationService.load_navigation()
        
        # Generate a unique ID
        new_id = str(uuid.uuid4().int)[:8]  # Use first 8 digits of UUID as ID
        
        # Create the new item
        new_item = {
            'id': new_id,
            'title': item_data.get('title', ''),
            'access': item_data.get('access', 'user'),
        }
        
        # Add page if provided
        if 'page' in item_data and item_data['page']:
            new_item['page'] = item_data['page']
        
        # Add to parent if specified
        if parent_id:
            def add_to_parent(items, target_parent_id):
                for item in items:
                    if 'id' in item and item['id'] == target_parent_id:
                        if 'children' not in item:
                            item['children'] = []
                        item['children'].append(new_item)
                        return True
                    if 'children' in item and item['children']:
                        if add_to_parent(item['children'], target_parent_id):
                            return True
                return False
            
            add_to_parent(navigation_data, parent_id)
        else:
            # Add to top level
            navigation_data.append(new_item)
        
        # Save the updated navigation data
        NavigationService.save_navigation(navigation_data)
        
        return new_item
    
    @staticmethod
    def update_item(item_id, item_data, new_parent_id=None):
        """Update a navigation item"""
        navigation_data = NavigationService.load_navigation()
        
        # Find the item to update
        def find_item(items, target_id, parent=None):
            for i, item in enumerate(items):
                if 'id' in item and item['id'] == target_id:
                    return item, parent, items, i
                if 'children' in item and item['children']:
                    result = find_item(item['children'], target_id, item)
                    if result[0]:
                        return result
            return None, None, None, None
        
        item_to_update, current_parent, parent_list, item_index = find_item(navigation_data, item_id)
        
        if not item_to_update:
            return None
        
        # Update item properties
        item_to_update['title'] = item_data.get('title', item_to_update.get('title', ''))
        item_to_update['access'] = item_data.get('access', item_to_update.get('access', 'user'))
        
        # Update page if provided
        if 'page' in item_data:
            if item_data['page']:
                item_to_update['page'] = item_data['page']
            elif 'page' in item_to_update:
                del item_to_update['page']
        
        # Handle parent change if needed
        current_parent_id = current_parent['id'] if current_parent else None
        
        if new_parent_id != current_parent_id:
            # Remove from current parent
            def remove_from_parent(items, target_id):
                for i, item in enumerate(items):
                    if 'id' in item and item['id'] == target_id:
                        return items.pop(i)
                    if 'children' in item and item['children']:
                        result = remove_from_parent(item['children'], target_id)
                        if result:
                            return result
                return None
            
            # Add to new parent
            def add_to_parent(items, target_parent_id, item_to_move):
                for item in items:
                    if 'id' in item and item['id'] == target_parent_id:
                        if 'children' not in item:
                            item['children'] = []
                        item['children'].append(item_to_move)
                        return True
                    if 'children' in item and item['children']:
                        if add_to_parent(item['children'], target_parent_id, item_to_move):
                            return True
                return False
            
            # Move to top level
            def move_to_top_level(items, target_id):
                for i, item in enumerate(items):
                    if 'id' in item and item['id'] == target_id:
                        return items.pop(i)
                    if 'children' in item and item['children']:
                        result = move_to_top_level(item['children'], target_id)
                        if result:
                            return result
                return None
            
            if current_parent:
                # Remove from current parent
                remove_from_parent(navigation_data, item_id)
            
            if new_parent_id:
                # Add to new parent
                add_to_parent(navigation_data, new_parent_id, item_to_update)
            else:
                # Move to top level
                move_to_top_level(navigation_data, item_id)
                navigation_data.append(item_to_update)
        
        # Save the updated navigation data
        NavigationService.save_navigation(navigation_data)
        
        return item_to_update
    
    @staticmethod
    def delete_item(item_id):
        """Delete a navigation item"""
        navigation_data = NavigationService.load_navigation()
        
        # Remove the item
        def remove_item(items, target_id):
            for i, item in enumerate(items):
                if 'id' in item and item['id'] == target_id:
                    return items.pop(i)
                if 'children' in item and item['children']:
                    result = remove_item(item['children'], target_id)
                    if result:
                        return result
            return None
        
        item = remove_item(navigation_data, item_id)
        
        if not item:
            return False
        
        # Save the updated navigation data
        NavigationService.save_navigation(navigation_data)
        
        return True
    
    @staticmethod
    def reorder_items(order):
        """Reorder navigation items by IDs"""
        navigation_data = NavigationService.load_navigation()
        
        # Create a map of id to item
        item_map = {}
        
        def map_items(items):
            for item in items:
                if 'id' in item:
                    item_map[item['id']] = item
                if 'children' in item and item['children']:
                    map_items(item['children'])
        
        map_items(navigation_data)
        
        # Create new list in the specified order
        new_items = []
        for item_id in order:
            if item_id in item_map:
                new_items.append(item_map[item_id])
        
        # Save the updated navigation data
        NavigationService.save_navigation(new_items)
        
        return True
    
    @staticmethod
    def get_parent_options(exclude_id=None):
        """Get parent options for dropdown"""
        navigation_data = NavigationService.load_navigation()
        parent_options = []
        
        def add_parent_options(items, level=0, exclude_id=None):
            for item in items:
                if 'id' in item and item['id'] != exclude_id:
                    parent_options.append({
                        'id': item['id'],
                        'title': '  ' * level + item['title']
                    })
                    if 'children' in item and item['children']:
                        add_parent_options(item['children'], level + 1, exclude_id)
        
        add_parent_options(navigation_data, exclude_id=exclude_id)
        
        return parent_options 