# Chayannito 26 Order Management System with Email Notifications

This repository contains an order management dashboard with an integrated email notification system that sends beautiful HTML email confirmations to customers when orders are placed.

## Features

- **Order Management Dashboard**: Web-based interface for viewing and managing orders
- **Email Notifications**: Automatic email confirmations sent via ZeptoMail
- **Beautiful Email Templates**: Professional HTML email templates with order details
- **Robust Error Handling**: Graceful degradation when email service is unavailable
- **Real-time Status**: Live status indicator showing email service availability

## Components

### 1. Order Dashboard (`index.html`)
- Firebase-based order management interface
- Real-time order updates
- Admin authentication
- Status management

### 2. Email Service (`email_server.py`)
- Python Flask server for handling email notifications
- ZeptoMail integration
- HTML email template rendering
- RESTful API endpoints

### 3. Email Template (`email_template.html`)
- Beautiful, responsive HTML email template
- Includes all order details (ID, customer info, items, totals)
- Professional styling with gradients and proper formatting

### 4. Frontend Integration (`email-service.js`)
- JavaScript client for email service integration
- Health monitoring
- Status indicators
- Test functionality

## Quick Start

### Prerequisites
- Python 3.7+
- ZeptoMail account and API key

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd orders
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure email settings**
   ```bash
   cp .env.example .env
   # Edit .env with your actual ZeptoMail API key
   ```

4. **Start the email service**
   ```bash
   python email_server.py
   ```
   The service will run on `http://localhost:5000`

5. **Open the dashboard**
   Open `index.html` in your browser or serve it via a web server

## Email Service API

### Endpoints

#### `GET /`
Health check endpoint
```json
{
  "status": "healthy",
  "service": "Chayannito 26 Email Notification Service",
  "timestamp": "2024-01-01T12:00:00.000000",
  "version": "1.0.0"
}
```

#### `POST /send-order-email`
Send order confirmation email
```json
{
  "orderId": "ORDER-123",
  "customerInfo": {
    "name": "Customer Name",
    "email": "customer@example.com",
    "phone": "+1234567890",
    "roll": "CS-2021-001",
    "department": "Computer Science",
    "bkashTransactionId": "TXN123456"
  },
  "items": [
    {
      "name": "Product Name",
      "selectedVariation": "Large",
      "quantity": 2,
      "price": 500
    }
  ],
  "total": 1000,
  "discount": 100,
  "finalTotal": 900,
  "status": "pending",
  "orderDate": "2024-01-01T12:00:00Z"
}
```

#### `POST /test-email`
Send test email
```json
{
  "test_email": "test@example.com"
}
```

#### `POST /preview-email`
Preview email template (returns HTML)

## Email Template Features

The email template includes:

- **Professional Header**: Gradient background with branding
- **Order Summary**: Order ID, date, status, customer information
- **Detailed Item List**: All ordered items with variations and pricing
- **Pricing Breakdown**: Subtotal, discounts, and final total
- **Coupon Information**: Applied coupons and discounts
- **Contact Information**: Support contact details
- **Responsive Design**: Works on all devices and email clients

## Integration with Order System

The email system automatically integrates with the existing Firebase-based order management system:

1. **Automatic Detection**: The dashboard detects if the email service is running
2. **Status Indicator**: Shows real-time email service status
3. **Graceful Degradation**: Orders work normally even when email service is offline
4. **Test Functionality**: Built-in test email feature

## Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```env
# ZeptoMail API Configuration
ZEPTOMAIL_API_KEY=your_api_key_here

# Email Configuration
FROM_EMAIL=registration@chayannito26.com
FROM_NAME=Chayannito 26 Registration

# Server Configuration
FLASK_ENV=development
FLASK_DEBUG=true
```

### Email Template Customization

The email template (`email_template.html`) can be customized:

- **Styling**: Modify the CSS in the `<style>` section
- **Content**: Update the HTML structure
- **Branding**: Change colors, fonts, and layout
- **Language**: Translate text content

## Troubleshooting

### Email Service Not Available
- Ensure Python dependencies are installed: `pip install -r requirements.txt`
- Check if the service is running: `python email_server.py`
- Verify the service is accessible: `curl http://localhost:5000`

### Emails Not Sending
- Check ZeptoMail API key in `.env` file
- Verify internet connection
- Check service logs in `email_server.log`
- Ensure customer email addresses are valid

### Email Template Issues
- Check `email_template.html` for syntax errors
- Test template with preview endpoint: `POST /preview-email`
- Verify Jinja2 template syntax

## Logs

The email service creates detailed logs in `email_server.log`:
- Email sending attempts
- Errors and warnings
- Service startup and health checks

## Security Notes

- The ZeptoMail API key should be kept secure
- Use environment variables for sensitive configuration
- Consider implementing rate limiting for production use
- Validate all input data before processing

## Development

### Adding New Features

1. **New Email Templates**: Create additional HTML templates
2. **Custom Email Logic**: Extend the `EmailService` class
3. **Additional Endpoints**: Add new Flask routes
4. **Frontend Integration**: Extend `email-service.js`

### Testing

```bash
# Test email service health
curl http://localhost:5000

# Send test email
curl -X POST http://localhost:5000/test-email \
  -H "Content-Type: application/json" \
  -d '{"test_email": "your-email@example.com"}'

# Preview email template
curl -X POST http://localhost:5000/preview-email \
  -H "Content-Type: application/json" \
  -d '{}' > preview.html
```

## License

This project is part of the Chayannito 26 order management system.