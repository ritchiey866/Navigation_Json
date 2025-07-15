/**
 * Navigation API Client
 * 
 * This module provides functions to interact with the navigation API endpoints.
 */

const NavigationAPI = {
    /**
     * Get all navigation items
     * @returns {Promise} Promise that resolves to the navigation items
     */
    getAllItems: async function() {
        try {
            const response = await fetch('/api/navigation/items');
            const data = await response.json();
            
            if (!data.success) {
                throw new Error(data.message || 'Failed to get navigation items');
            }
            
            return data.items;
        } catch (error) {
            console.error('Error getting navigation items:', error);
            throw error;
        }
    },
    
    /**
     * Get a navigation item by ID
     * @param {string} itemId - The ID of the item to get
     * @returns {Promise} Promise that resolves to the navigation item
     */
    getItemById: async function(itemId) {
        try {
            const response = await fetch(`/api/navigation/items/${itemId}`);
            const data = await response.json();
            
            if (!data.success) {
                throw new Error(data.message || 'Failed to get navigation item');
            }
            
            return data.item;
        } catch (error) {
            console.error('Error getting navigation item:', error);
            throw error;
        }
    },
    
    /**
     * Create a new navigation item
     * @param {Object} itemData - The data for the new item
     * @returns {Promise} Promise that resolves to the created item
     */
    createItem: async function(itemData) {
        try {
            const response = await fetch('/api/navigation/items', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(itemData)
            });
            
            const data = await response.json();
            
            if (!data.success) {
                throw new Error(data.message || 'Failed to create navigation item');
            }
            
            return data.item;
        } catch (error) {
            console.error('Error creating navigation item:', error);
            throw error;
        }
    },
    
    /**
     * Update a navigation item
     * @param {string} itemId - The ID of the item to update
     * @param {Object} itemData - The updated data for the item
     * @returns {Promise} Promise that resolves to the updated item
     */
    updateItem: async function(itemId, itemData) {
        try {
            const response = await fetch(`/api/navigation/items/${itemId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(itemData)
            });
            
            const data = await response.json();
            
            if (!data.success) {
                throw new Error(data.message || 'Failed to update navigation item');
            }
            
            return data.item;
        } catch (error) {
            console.error('Error updating navigation item:', error);
            throw error;
        }
    },
    
    /**
     * Delete a navigation item
     * @param {string} itemId - The ID of the item to delete
     * @returns {Promise} Promise that resolves when the item is deleted
     */
    deleteItem: async function(itemId) {
        try {
            const response = await fetch(`/api/navigation/items/${itemId}`, {
                method: 'DELETE'
            });
            
            const data = await response.json();
            
            if (!data.success) {
                throw new Error(data.message || 'Failed to delete navigation item');
            }
            
            return true;
        } catch (error) {
            console.error('Error deleting navigation item:', error);
            throw error;
        }
    },
    
    /**
     * Reorder navigation items
     * @param {Array} order - Array of item IDs in the desired order
     * @returns {Promise} Promise that resolves when the items are reordered
     */
    reorderItems: async function(order) {
        try {
            const response = await fetch('/api/navigation/reorder', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ order })
            });
            
            const data = await response.json();
            
            if (!data.success) {
                throw new Error(data.message || 'Failed to reorder navigation items');
            }
            
            return true;
        } catch (error) {
            console.error('Error reordering navigation items:', error);
            throw error;
        }
    },
    
    /**
     * Get parent options for dropdown
     * @param {string} excludeId - ID to exclude from the options (optional)
     * @returns {Promise} Promise that resolves to the parent options
     */
    getParentOptions: async function(excludeId = null) {
        try {
            let url = '/api/navigation/parent-options';
            
            if (excludeId) {
                url += `?exclude_id=${excludeId}`;
            }
            
            const response = await fetch(url);
            const data = await response.json();
            
            if (!data.success) {
                throw new Error(data.message || 'Failed to get parent options');
            }
            
            return data.parent_options;
        } catch (error) {
            console.error('Error getting parent options:', error);
            throw error;
        }
    }
};

// Export the module
export default NavigationAPI; 