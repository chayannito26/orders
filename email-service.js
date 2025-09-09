/**
 * Email Service Integration for Chayannito 26 Orders
 * Provides functionality to send email notifications when the email server is running
 */

class EmailServiceClient {
    constructor(baseUrl = 'http://localhost:5000') {
        this.baseUrl = baseUrl;
        this.isAvailable = false;
        this.checkServiceHealth();
    }

    /**
     * Check if the email service is running and available
     */
    async checkServiceHealth() {
        try {
            const response = await fetch(`${this.baseUrl}/`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
                // Add timeout to avoid hanging
                signal: AbortSignal.timeout(5000)
            });
            
            if (response.ok) {
                const data = await response.json();
                this.isAvailable = data.status === 'healthy';
                console.log('Email service is available:', this.isAvailable);
            } else {
                this.isAvailable = false;
                console.log('Email service health check failed:', response.status);
            }
        } catch (error) {
            this.isAvailable = false;
            console.log('Email service is not available:', error.message);
        }
        
        // Update UI to show email service status
        this.updateEmailServiceStatus();
    }

    /**
     * Update the UI to show email service status
     */
    updateEmailServiceStatus() {
        // Remove existing status indicator
        const existingIndicator = document.getElementById('email-service-status');
        if (existingIndicator) {
            existingIndicator.remove();
        }

        // Create new status indicator
        const statusIndicator = document.createElement('div');
        statusIndicator.id = 'email-service-status';
        statusIndicator.className = `fixed top-4 right-4 z-50 px-3 py-2 rounded-md text-sm font-medium ${
            this.isAvailable 
                ? 'bg-green-100 text-green-800 border border-green-200' 
                : 'bg-gray-100 text-gray-600 border border-gray-200'
        }`;
        
        statusIndicator.innerHTML = this.isAvailable 
            ? '🟢 Email Service: Online'
            : '🔴 Email Service: Offline';
        
        // Add tooltip
        statusIndicator.title = this.isAvailable 
            ? 'Email notifications will be sent for new orders'
            : 'Email notifications are currently unavailable';
        
        document.body.appendChild(statusIndicator);

        // Auto-hide after 5 seconds if offline (to reduce clutter)
        if (!this.isAvailable) {
            setTimeout(() => {
                if (statusIndicator && statusIndicator.parentNode) {
                    statusIndicator.style.opacity = '0.7';
                }
            }, 5000);
        }
    }

    /**
     * Send order confirmation email
     * @param {Object} orderData - The order data to send
     * @returns {Promise<Object>} - Result of the email operation
     */
    async sendOrderEmail(orderData) {
        if (!this.isAvailable) {
            console.log('Email service not available, skipping email notification');
            return {
                success: false,
                error: 'Email service not available',
                skipped: true
            };
        }

        try {
            const response = await fetch(`${this.baseUrl}/send-order-email`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(orderData),
                signal: AbortSignal.timeout(30000) // 30 second timeout
            });

            const result = await response.json();
            
            if (result.success) {
                console.log('Order email sent successfully:', result);
                this.showEmailNotification('✅ Order confirmation email sent!', 'success');
            } else {
                console.error('Failed to send order email:', result);
                this.showEmailNotification('⚠️ Failed to send email notification', 'warning');
            }
            
            return result;
            
        } catch (error) {
            console.error('Error sending order email:', error);
            this.showEmailNotification('❌ Email service error', 'error');
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * Test email functionality
     * @param {string} testEmail - Email address to send test email to
     * @returns {Promise<Object>} - Result of the test operation
     */
    async testEmail(testEmail = 'test@example.com') {
        if (!this.isAvailable) {
            this.showEmailNotification('Email service is not available', 'error');
            return { success: false, error: 'Email service not available' };
        }

        try {
            const response = await fetch(`${this.baseUrl}/test-email`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ test_email: testEmail }),
                signal: AbortSignal.timeout(30000)
            });

            const result = await response.json();
            
            if (result.success) {
                this.showEmailNotification(`✅ Test email sent to ${testEmail}!`, 'success');
            } else {
                this.showEmailNotification('❌ Failed to send test email', 'error');
            }
            
            return result;
            
        } catch (error) {
            console.error('Error sending test email:', error);
            this.showEmailNotification('❌ Email test failed', 'error');
            return { success: false, error: error.message };
        }
    }

    /**
     * Show a notification about email operations
     * @param {string} message - The message to show
     * @param {string} type - The type of notification (success, warning, error)
     */
    showEmailNotification(message, type = 'info') {
        // Remove existing notification
        const existingNotification = document.getElementById('email-notification');
        if (existingNotification) {
            existingNotification.remove();
        }

        // Create notification element
        const notification = document.createElement('div');
        notification.id = 'email-notification';
        notification.className = 'fixed top-20 right-4 z-50 max-w-sm p-4 rounded-md shadow-lg transition-all duration-300';
        
        // Set colors based on type
        const colors = {
            success: 'bg-green-100 text-green-800 border border-green-200',
            warning: 'bg-yellow-100 text-yellow-800 border border-yellow-200',
            error: 'bg-red-100 text-red-800 border border-red-200',
            info: 'bg-blue-100 text-blue-800 border border-blue-200'
        };
        
        notification.className += ` ${colors[type] || colors.info}`;
        notification.innerHTML = `
            <div class="flex items-center">
                <span class="flex-1">${message}</span>
                <button onclick="this.parentElement.parentElement.remove()" class="ml-2 text-lg leading-none">&times;</button>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification && notification.parentNode) {
                notification.style.opacity = '0';
                setTimeout(() => {
                    if (notification && notification.parentNode) {
                        notification.remove();
                    }
                }, 300);
            }
        }, 5000);
    }

    /**
     * Refresh service health status
     */
    async refreshStatus() {
        this.showEmailNotification('Checking email service status...', 'info');
        await this.checkServiceHealth();
    }
}

// Initialize email service client
const emailService = new EmailServiceClient();

// Add email service controls to the page
function addEmailServiceControls() {
    // Check if controls already exist
    if (document.getElementById('email-service-controls')) {
        return;
    }

    // Find a good place to add controls (after the header)
    const header = document.querySelector('header');
    if (!header) {
        console.log('Header not found, email controls not added');
        return;
    }

    // Create email service controls container
    const controlsContainer = document.createElement('div');
    controlsContainer.id = 'email-service-controls';
    controlsContainer.className = 'bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-6';
    controlsContainer.innerHTML = `
        <div class="flex items-center justify-between">
            <div>
                <h3 class="text-lg font-semibold text-gray-900">Email Notifications</h3>
                <p class="text-sm text-gray-600">Send order confirmations via email</p>
            </div>
            <div class="flex gap-2">
                <button id="refresh-email-status" class="bg-blue-600 text-white px-3 py-2 rounded-md text-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500">
                    Refresh Status
                </button>
                <button id="test-email-btn" class="bg-green-600 text-white px-3 py-2 rounded-md text-sm hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500">
                    Test Email
                </button>
            </div>
        </div>
    `;

    // Insert after header
    header.parentNode.insertBefore(controlsContainer, header.nextSibling);

    // Add event listeners
    document.getElementById('refresh-email-status').addEventListener('click', () => {
        emailService.refreshStatus();
    });

    document.getElementById('test-email-btn').addEventListener('click', () => {
        const testEmail = prompt('Enter email address for test email:', 'test@example.com');
        if (testEmail) {
            emailService.testEmail(testEmail);
        }
    });
}

// Function to monitor for new orders and send emails
function setupOrderEmailMonitoring() {
    // This function should be called when a new order is detected
    // It integrates with the existing Firebase listener
    
    // Store original onSnapshot callback to enhance it
    window.originalOnSnapshotCallback = null;
    
    // Function to send email for new orders
    window.sendEmailForNewOrder = function(orderData) {
        if (emailService.isAvailable && orderData.customerInfo && orderData.customerInfo.email) {
            console.log('Sending email for new order:', orderData.id);
            emailService.sendOrderEmail(orderData);
        } else if (!emailService.isAvailable) {
            console.log('Email service not available, skipping email for order:', orderData.id);
        } else {
            console.log('No customer email provided for order:', orderData.id);
        }
    };
}

// Initialize when DOM is loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        addEmailServiceControls();
        setupOrderEmailMonitoring();
    });
} else {
    addEmailServiceControls();
    setupOrderEmailMonitoring();
}

// Periodically check email service health (every 5 minutes)
setInterval(() => {
    emailService.checkServiceHealth();
}, 5 * 60 * 1000);

// Export for use in other scripts
window.emailService = emailService;