#!/usr/bin/env python3
"""
Email Notification Server for Chayannito 26 Orders
Sends beautiful HTML email notifications using ZeptoMail when orders are placed.
"""

import json
import logging
import os
import requests
from datetime import datetime
from typing import Dict, Any, Optional

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from jinja2 import Template
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('email_server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='.', static_url_path='')  # Serve static files from current directory
CORS(app)  # Enable CORS for all routes

# Configuration
ZEPTOMAIL_URL = "https://api.zeptomail.com/v1.1/email"
ZEPTOMAIL_API_KEY = os.getenv('ZEPTOMAIL_API_KEY', 'wSsVR60jrBP3W691zmeqde9qyAwHDl3/Ekl60FqjunP/GqyWpcdolkLJUQLzGPZKEG46RTsV97wgyh4IgzRf2o8tmQ1SWiiF9mqRe1U4J3x17qnvhDzOVmRdlRKALIILxg5umWZoE8oh+g==')
FROM_EMAIL = os.getenv('FROM_EMAIL', 'registration@chayannito26.com')
FROM_NAME = os.getenv('FROM_NAME', 'Chayannito 26 Registration')

class EmailService:
    """Email service for sending order notifications via ZeptoMail"""
    
    def __init__(self):
        self.headers = {
            'accept': "application/json",
            'content-type': "application/json",
            'authorization': f"Zoho-enczapikey {ZEPTOMAIL_API_KEY}",
        }
        self.email_template = self._load_email_template()
    
    def _load_email_template(self) -> str:
        """Load the HTML email template"""
        try:
            template_path = os.path.join(os.path.dirname(__file__), 'email_template.html')
            with open(template_path, 'r', encoding='utf-8') as file:
                return file.read()
        except FileNotFoundError:
            logger.error("Email template file not found")
            return "<h1>Order Confirmation</h1><p>Thank you for your order!</p>"
    
    def _format_order_data(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format order data for email template"""
        # Format the order date
        order_date = order_data.get('orderDate', '')
        try:
            if order_date:
                dt = datetime.fromisoformat(order_date.replace('Z', '+00:00'))
                formatted_date = dt.strftime('%B %d, %Y at %I:%M %p')
            else:
                formatted_date = 'N/A'
        except (ValueError, AttributeError):
            formatted_date = str(order_date) if order_date else 'N/A'
        
        # Create a copy of order data with formatted date
        formatted_order = order_data.copy()
        formatted_order['formatted_date'] = formatted_date
        
        # Ensure required fields exist with defaults
        if 'customerInfo' not in formatted_order:
            formatted_order['customerInfo'] = {}
        
        customer_info = formatted_order['customerInfo']
        defaults = {
            'name': 'N/A',
            'email': '',
            'phone': 'N/A',
            'roll': 'N/A',
            'department': 'N/A',
            'bkashTransactionId': 'N/A'
        }
        
        for key, default_value in defaults.items():
            if key not in customer_info:
                customer_info[key] = default_value
        
        # Ensure items exist and format them
        if 'items' not in formatted_order:
            formatted_order['items'] = []
        
        # Format each item to ensure proper data types
        for item in formatted_order['items']:
            if not isinstance(item, dict):
                continue
            # Ensure quantity is a number
            try:
                item['quantity'] = int(item.get('quantity', 0))
            except (ValueError, TypeError):
                item['quantity'] = 0
            # Ensure price is a number  
            try:
                item['price'] = float(item.get('price', 0))
            except (ValueError, TypeError):
                item['price'] = 0
            # Calculate item total
            item['total'] = item['quantity'] * item['price']
        
        # Ensure numeric fields
        numeric_fields = ['total', 'discount', 'finalTotal']
        for field in numeric_fields:
            if field not in formatted_order:
                formatted_order[field] = 0
            try:
                formatted_order[field] = float(formatted_order[field])
            except (ValueError, TypeError):
                formatted_order[field] = 0
        
        # Calculate final total if not provided
        if not formatted_order['finalTotal']:
            total = formatted_order.get('total', 0)
            discount = formatted_order.get('discount', 0)
            formatted_order['finalTotal'] = max(0, total - discount)
        
        # Ensure appliedCoupon is a dict or None
        if 'appliedCoupon' not in formatted_order:
            formatted_order['appliedCoupon'] = None
        elif formatted_order['appliedCoupon'] and not isinstance(formatted_order['appliedCoupon'], dict):
            formatted_order['appliedCoupon'] = None
        
        return formatted_order
    
    def _render_email_html(self, order_data: Dict[str, Any]) -> str:
        """Render the email HTML template with order data"""
        try:
            template = Template(self.email_template)
            formatted_order = self._format_order_data(order_data)
            logger.info(f"Rendering template with order data keys: {list(formatted_order.keys())}")
            
            # Convert to a simple namespace object to avoid dict.items() confusion
            def dict_to_namespace(d):
                """Recursively convert dict to namespace object"""
                if isinstance(d, dict):
                    class Namespace:
                        pass
                    obj = Namespace()
                    for key, value in d.items():
                        setattr(obj, key, dict_to_namespace(value))
                    return obj
                elif isinstance(d, list):
                    return [dict_to_namespace(item) for item in d]
                else:
                    return d
            
            order_obj = dict_to_namespace(formatted_order)
            
            return template.render(order=order_obj)
        except Exception as e:
            logger.error(f"Error rendering email template: {e}")
            logger.error(f"Order data: {order_data}")
            return f"<h1>Order Confirmation</h1><p>Order ID: {order_data.get('orderId', 'N/A')}</p>"
    
    def send_order_email(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send order confirmation email"""
        try:
            # Get customer email
            customer_info = order_data.get('customerInfo', {})
            customer_email = customer_info.get('email')
            customer_name = customer_info.get('name', 'Customer')
            order_id = order_data.get('orderId') or order_data.get('orderID', 'N/A')
            
            if not customer_email:
                return {
                    'success': False,
                    'error': 'Customer email not provided',
                    'order_id': order_id
                }
            
            # Render email HTML
            html_content = self._render_email_html(order_data)
            
            # Prepare email payload
            payload = json.dumps({
                "from": {
                    "address": FROM_EMAIL,
                    "name": FROM_NAME
                },
                "to": [{
                    "email_address": {
                        "address": customer_email,
                        "name": customer_name
                    }
                }],
                "subject": f"Order Confirmation - {order_id}",
                "htmlbody": html_content
            })
            
            # Send email
            response = requests.post(ZEPTOMAIL_URL, data=payload, headers=self.headers, timeout=30)
            
            if response.status_code == 201:
                logger.info(f"Email sent successfully for order {order_id} to {customer_email}")
                return {
                    'success': True,
                    'message': 'Email sent successfully',
                    'order_id': order_id,
                    'email': customer_email
                }
            else:
                logger.error(f"Failed to send email for order {order_id}. Status: {response.status_code}, Response: {response.text}")
                return {
                    'success': False,
                    'error': f'Email service returned status {response.status_code}',
                    'order_id': order_id,
                    'details': response.text
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error sending email for order {order_data.get('orderId', 'N/A')}: {e}")
            return {
                'success': False,
                'error': f'Network error: {str(e)}',
                'order_id': order_data.get('orderId', 'N/A')
            }
        except Exception as e:
            logger.error(f"Unexpected error sending email for order {order_data.get('orderId', 'N/A')}: {e}")
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}',
                'order_id': order_data.get('orderId', 'N/A')
            }

# Initialize email service
email_service = EmailService()


# Serve index.html at root
@app.route('/', methods=['GET'])
def serve_index():
    """Serve the order dashboard (index.html) at root."""
    index_path = os.path.join(os.path.dirname(__file__), 'index.html')
    try:
        with open(index_path, 'r', encoding='utf-8') as f:
            html = f.read()
        return html, 200, {'Content-Type': 'text/html'}
    except Exception as e:
        logger.error(f"Error serving index.html: {e}")
        return f"<h1>Error loading dashboard</h1><p>{str(e)}</p>", 500, {'Content-Type': 'text/html'}

# Status endpoint
@app.route('/status', methods=['GET'])
def status():
    """Status endpoint for health checks."""
    return jsonify({
        'status': 'healthy',
        'service': 'Chayannito 26 Email Notification Service',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/send-order-email', methods=['POST'])
def send_order_email():
    """Send order confirmation email"""
    try:
        # Get order data from request
        if not request.is_json:
            return jsonify({
                'success': False,
                'error': 'Request must be JSON'
            }), 400
        
        order_data = request.get_json()
        
        if not order_data:
            return jsonify({
                'success': False,
                'error': 'No order data provided'
            }), 400
        
        # Send email
        result = email_service.send_order_email(order_data)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Error in send_order_email endpoint: {e}")
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

@app.route('/test-email', methods=['POST'])
def test_email():
    """Test email functionality with sample data"""
    try:
        # Sample order data for testing
        sample_order = {
            "orderId": "TEST-" + datetime.now().strftime("%Y%m%d-%H%M%S"),
            "orderDate": datetime.now().isoformat(),
            "status": "pending",
            "customerInfo": {
                "name": "Test Customer",
                "email": request.json.get('test_email', 'test@example.com') if request.is_json and request.json else 'test@example.com',
                "phone": "+1234567890",
                "roll": "CS-2021-001",
                "department": "Computer Science",
                "bkashTransactionId": "TXN123456789"
            },
            "items": [
                {
                    "name": "Test Product 1",
                    "selectedVariation": "Large",
                    "quantity": 2,
                    "price": 500
                },
                {
                    "name": "Test Product 2",
                    "quantity": 1,
                    "price": 300
                }
            ],
            "total": 1300,
            "discount": 100,
            "finalTotal": 1200,
            "appliedCoupon": {
                "code": "TESTCODE",
                "discountValue": 100
            }
        }
        
        # Send test email
        result = email_service.send_order_email(sample_order)
        return jsonify(result), 200 if result['success'] else 400
        
    except Exception as e:
        logger.error(f"Error in test_email endpoint: {e}")
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

@app.route('/preview-email', methods=['POST'])
def preview_email():
    """Preview email HTML template with provided order data"""
    try:
        order_data = {}
        if request.is_json and request.get_json():
            order_data = request.get_json()
        
        # Use sample data if no data provided
        if not order_data:
            order_data = {
                "orderId": "PREVIEW-001",
                "orderDate": datetime.now().isoformat(),
                "status": "pending",
                "customerInfo": {
                    "name": "Preview Customer",
                    "email": "preview@example.com",
                    "phone": "+1234567890",
                    "roll": "CS-2021-001",
                    "department": "Computer Science",
                    "bkashTransactionId": "TXN123456789"
                },
                "items": [
                    {
                        "name": "Sample Product",
                        "selectedVariation": "Medium",
                        "quantity": 1,
                        "price": 500
                    }
                ],
                "total": 500,
                "discount": 0,
                "finalTotal": 500
            }
        
        # Render and return HTML
        html_content = email_service._render_email_html(order_data)
        return html_content, 200, {'Content-Type': 'text/html'}
        
    except Exception as e:
        logger.error(f"Error in preview_email endpoint: {e}")
        return f"<h1>Error</h1><p>{str(e)}</p>", 500, {'Content-Type': 'text/html'}

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found',
        'available_endpoints': [
            'GET /',
            'POST /send-order-email',
            'POST /test-email',
            'POST /preview-email'
        ]
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

if __name__ == '__main__':
    logger.info("Starting Chayannito 26 Email Notification Service")
    logger.info(f"Service will run on http://localhost:5000")
    logger.info("Available endpoints:")
    logger.info("  GET  /                 - Health check")
    logger.info("  POST /send-order-email - Send order confirmation email")
    logger.info("  POST /test-email       - Test email functionality")
    logger.info("  POST /preview-email    - Preview email template")
    
    # Run the Flask app
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        use_reloader=False  # Disable reloader to avoid issues with logging
    )