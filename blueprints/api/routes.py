from flask import Blueprint, request, jsonify
from datetime import datetime

# Create the blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/verify', methods=['POST'])
def verify_data():
    data = request.json.get('data')
    
    # Simulate different types of verification results
    if data.lower() == 'error':
        result = {
            'status': 'error',
            'message': 'Invalid data format',
            'details': {
                'timestamp': datetime.now().isoformat(),
                'error_code': 'E001',
                'suggestions': ['Check input format', 'Ensure all required fields are filled']
            }
        }
    elif data.lower() == 'warning':
        result = {
            'status': 'warning',
            'message': 'Data verification incomplete',
            'details': {
                'timestamp': datetime.now().isoformat(),
                'missing_fields': ['email', 'phone'],
                'validation_results': [
                    {'field': 'name', 'status': 'valid'},
                    {'field': 'email', 'status': 'missing'},
                    {'field': 'phone', 'status': 'missing'}
                ]
            }
        }
    else:
        result = {
            'status': 'success',
            'message': 'Data verified successfully',
            'details': {
                'timestamp': datetime.now().isoformat(),
                'data_points': [
                    {'label': 'Input Value', 'value': data},
                    {'label': 'Length', 'value': len(data)},
                    {'label': 'Type', 'value': type(data).__name__}
                ],
                'metadata': {
                    'processed_by': 'verification_service',
                    'version': '1.0'
                }
            }
        }
    
    return jsonify(result) 