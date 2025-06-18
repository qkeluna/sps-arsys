"""
Email service for sending appointment notifications using Resend
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import resend
from jinja2 import Template

from ..config import settings


# Configure logging
logger = logging.getLogger(__name__)

# Initialize Resend
resend.api_key = settings.resend_api_key


class EmailService:
    """Email service for sending appointment-related emails"""

    def __init__(self):
        self.from_email = settings.from_email
        self.support_email = settings.support_email

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        reply_to: Optional[str] = None
    ) -> bool:
        """Send an email using Resend"""
        try:
            params = {
                "from": self.from_email,
                "to": [to_email],
                "subject": subject,
                "html": html_content,
                "reply_to": reply_to or self.support_email,
            }
            
            if text_content:
                params["text"] = text_content

            response = resend.emails.send(params)
            logger.info(f"Email sent successfully to {to_email}: {response}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False

    async def send_booking_confirmation(
        self,
        customer_email: str,
        customer_name: str,
        studio_name: str,
        appointment_date: str,
        appointment_time: str,
        session_type: str,
        total_price: float,
        appointment_id: str,
        studio_address: Optional[str] = None
    ) -> bool:
        """Send booking confirmation email"""
        
        subject = f"Booking Confirmation - {studio_name}"
        
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Booking Confirmation</title>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; }
                .container { max-width: 600px; margin: 0 auto; background: #f9f9f9; padding: 20px; border-radius: 10px; }
                .header { background: #4f46e5; color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }
                .content { background: white; padding: 30px; border-radius: 0 0 10px 10px; }
                .booking-details { background: #f0f9ff; padding: 20px; border-radius: 5px; margin: 20px 0; }
                .detail-row { display: flex; justify-content: space-between; margin: 10px 0; }
                .detail-label { font-weight: bold; }
                .button { background: #4f46e5; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 20px 0; }
                .footer { text-align: center; margin-top: 30px; color: #666; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Booking Confirmed! 🎉</h1>
                </div>
                <div class="content">
                    <p>Dear {{ customer_name }},</p>
                    
                    <p>Your photo session has been successfully booked at <strong>{{ studio_name }}</strong>!</p>
                    
                    <div class="booking-details">
                        <h3>Booking Details</h3>
                        <div class="detail-row">
                            <span class="detail-label">Booking ID:</span>
                            <span>{{ appointment_id }}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Date:</span>
                            <span>{{ appointment_date }}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Time:</span>
                            <span>{{ appointment_time }}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Session Type:</span>
                            <span>{{ session_type }}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Total Price:</span>
                            <span>${{ total_price }}</span>
                        </div>
                        {% if studio_address %}
                        <div class="detail-row">
                            <span class="detail-label">Location:</span>
                            <span>{{ studio_address }}</span>
                        </div>
                        {% endif %}
                    </div>
                    
                    <p><strong>What to bring:</strong></p>
                    <ul>
                        <li>A valid ID</li>
                        <li>Any props or outfits you'd like to use</li>
                        <li>Your creativity and smile! 📸</li>
                    </ul>
                    
                    <p>We're excited to see you soon! If you have any questions or need to make changes to your booking, please don't hesitate to contact us.</p>
                    
                    <a href="{{ frontend_url }}/booking/{{ appointment_id }}" class="button">View Booking Details</a>
                    
                    <div class="footer">
                        <p>Best regards,<br>{{ studio_name }} Team</p>
                        <p>Need help? Contact us at {{ support_email }}</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        template = Template(html_template)
        html_content = template.render(
            customer_name=customer_name,
            studio_name=studio_name,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            session_type=session_type,
            total_price=total_price,
            appointment_id=appointment_id,
            studio_address=studio_address,
            frontend_url=settings.frontend_url,
            support_email=self.support_email
        )
        
        return await self.send_email(
            to_email=customer_email,
            subject=subject,
            html_content=html_content
        )

    async def send_booking_reminder(
        self,
        customer_email: str,
        customer_name: str,
        studio_name: str,
        appointment_date: str,
        appointment_time: str,
        appointment_id: str,
        hours_until: int = 24
    ) -> bool:
        """Send booking reminder email"""
        
        subject = f"Reminder: Your photo session at {studio_name} is tomorrow"
        
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Booking Reminder</title>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; }
                .container { max-width: 600px; margin: 0 auto; background: #f9f9f9; padding: 20px; border-radius: 10px; }
                .header { background: #f59e0b; color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }
                .content { background: white; padding: 30px; border-radius: 0 0 10px 10px; }
                .reminder-box { background: #fef3c7; padding: 20px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #f59e0b; }
                .button { background: #f59e0b; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 20px 0; }
                .footer { text-align: center; margin-top: 30px; color: #666; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Don't Forget! 📸</h1>
                </div>
                <div class="content">
                    <p>Hi {{ customer_name }},</p>
                    
                    <p>This is a friendly reminder that your photo session at <strong>{{ studio_name }}</strong> is coming up!</p>
                    
                    <div class="reminder-box">
                        <h3>🗓️ Your Appointment</h3>
                        <p><strong>Date:</strong> {{ appointment_date }}</p>
                        <p><strong>Time:</strong> {{ appointment_time }}</p>
                        <p><strong>Studio:</strong> {{ studio_name }}</p>
                    </div>
                    
                    <p><strong>Please remember to:</strong></p>
                    <ul>
                        <li>Arrive 5-10 minutes early</li>
                        <li>Bring a valid ID</li>
                        <li>Come prepared with any props or outfits</li>
                        <li>Let us know if you're running late</li>
                    </ul>
                    
                    <p>We can't wait to capture some amazing photos with you!</p>
                    
                    <a href="{{ frontend_url }}/booking/{{ appointment_id }}" class="button">View Booking Details</a>
                    
                    <div class="footer">
                        <p>See you soon!<br>{{ studio_name }} Team</p>
                        <p>Need to reschedule? Contact us at {{ support_email }}</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        template = Template(html_template)
        html_content = template.render(
            customer_name=customer_name,
            studio_name=studio_name,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            appointment_id=appointment_id,
            frontend_url=settings.frontend_url,
            support_email=self.support_email
        )
        
        return await self.send_email(
            to_email=customer_email,
            subject=subject,
            html_content=html_content
        )

    async def send_booking_cancellation(
        self,
        customer_email: str,
        customer_name: str,
        studio_name: str,
        appointment_date: str,
        appointment_time: str,
        appointment_id: str,
        cancellation_reason: Optional[str] = None
    ) -> bool:
        """Send booking cancellation email"""
        
        subject = f"Booking Cancelled - {studio_name}"
        
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Booking Cancelled</title>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; }
                .container { max-width: 600px; margin: 0 auto; background: #f9f9f9; padding: 20px; border-radius: 10px; }
                .header { background: #dc2626; color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }
                .content { background: white; padding: 30px; border-radius: 0 0 10px 10px; }
                .cancellation-box { background: #fef2f2; padding: 20px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #dc2626; }
                .button { background: #4f46e5; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 20px 0; }
                .footer { text-align: center; margin-top: 30px; color: #666; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Booking Cancelled</h1>
                </div>
                <div class="content">
                    <p>Dear {{ customer_name }},</p>
                    
                    <p>Your booking at <strong>{{ studio_name }}</strong> has been cancelled.</p>
                    
                    <div class="cancellation-box">
                        <h3>Cancelled Appointment</h3>
                        <p><strong>Booking ID:</strong> {{ appointment_id }}</p>
                        <p><strong>Date:</strong> {{ appointment_date }}</p>
                        <p><strong>Time:</strong> {{ appointment_time }}</p>
                        {% if cancellation_reason %}
                        <p><strong>Reason:</strong> {{ cancellation_reason }}</p>
                        {% endif %}
                    </div>
                    
                    <p>If you'd like to reschedule or book a new appointment, we'd love to have you back!</p>
                    
                    <a href="{{ frontend_url }}/book/{{ studio_slug }}" class="button">Book New Appointment</a>
                    
                    <div class="footer">
                        <p>Thank you for your understanding,<br>{{ studio_name }} Team</p>
                        <p>Questions? Contact us at {{ support_email }}</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        template = Template(html_template)
        html_content = template.render(
            customer_name=customer_name,
            studio_name=studio_name,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            appointment_id=appointment_id,
            cancellation_reason=cancellation_reason,
            frontend_url=settings.frontend_url,
            support_email=self.support_email
        )
        
        return await self.send_email(
            to_email=customer_email,
            subject=subject,
            html_content=html_content
        )

    async def send_studio_notification(
        self,
        studio_email: str,
        studio_name: str,
        customer_name: str,
        customer_email: str,
        appointment_date: str,
        appointment_time: str,
        session_type: str,
        appointment_id: str,
        notification_type: str = "new_booking"
    ) -> bool:
        """Send notification to studio owner"""
        
        if notification_type == "new_booking":
            subject = f"New Booking - {customer_name}"
        elif notification_type == "cancellation":
            subject = f"Booking Cancelled - {customer_name}"
        else:
            subject = f"Booking Update - {customer_name}"
        
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>{{ subject }}</title>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; }
                .container { max-width: 600px; margin: 0 auto; background: #f9f9f9; padding: 20px; border-radius: 10px; }
                .header { background: #10b981; color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }
                .content { background: white; padding: 30px; border-radius: 0 0 10px 10px; }
                .booking-details { background: #f0fdf4; padding: 20px; border-radius: 5px; margin: 20px 0; }
                .detail-row { display: flex; justify-content: space-between; margin: 10px 0; }
                .detail-label { font-weight: bold; }
                .button { background: #10b981; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 20px 0; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{{ notification_title }}</h1>
                </div>
                <div class="content">
                    <p>Hello {{ studio_name }},</p>
                    
                    <p>{{ notification_message }}</p>
                    
                    <div class="booking-details">
                        <h3>Booking Details</h3>
                        <div class="detail-row">
                            <span class="detail-label">Customer:</span>
                            <span>{{ customer_name }}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Email:</span>
                            <span>{{ customer_email }}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Date:</span>
                            <span>{{ appointment_date }}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Time:</span>
                            <span>{{ appointment_time }}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Session Type:</span>
                            <span>{{ session_type }}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Booking ID:</span>
                            <span>{{ appointment_id }}</span>
                        </div>
                    </div>
                    
                    <a href="{{ frontend_url }}/dashboard/appointments" class="button">Manage Bookings</a>
                </div>
            </div>
        </body>
        </html>
        """
        
        if notification_type == "new_booking":
            notification_title = "New Booking Received! 🎉"
            notification_message = f"You have a new booking from {customer_name}."
        elif notification_type == "cancellation":
            notification_title = "Booking Cancelled"
            notification_message = f"{customer_name} has cancelled their booking."
        else:
            notification_title = "Booking Updated"
            notification_message = f"Booking details have been updated for {customer_name}."
        
        template = Template(html_template)
        html_content = template.render(
            subject=subject,
            notification_title=notification_title,
            notification_message=notification_message,
            studio_name=studio_name,
            customer_name=customer_name,
            customer_email=customer_email,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            session_type=session_type,
            appointment_id=appointment_id,
            frontend_url=settings.frontend_url
        )
        
        return await self.send_email(
            to_email=studio_email,
            subject=subject,
            html_content=html_content
        )


# Global email service instance
email_service = EmailService() 