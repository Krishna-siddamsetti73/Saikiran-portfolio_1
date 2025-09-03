from flask import Flask, request, jsonify
from flask_cors import CORS
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv
# Add to your Flask app
import json
from datetime import datetime

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration - Replace with your actual credentials
WHATSAPP_NUMBER = "+919347834548"
EMAIL_USER = os.getenv("EMAIL_USER")  # Your Gmail address
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")  # Your Google App Password

@app.route('/send-message', methods=['POST'])
def send_message():
    try:
        data = request.get_json()
        
        name = data.get('name')
        email = data.get('email')
        subject = data.get('subject', 'Project Inquiry')
        message = data.get('message')
        
        # Validate required fields
        if not all([name, email, message]):
            return jsonify({"error": "Missing required fields"}), 400
        
        # 1. Send WhatsApp message
        save_contact_to_file(name, email, subject, message)
        
        # 2. Send thank you email
        send_thankyou_email(name, email)
        
        return jsonify({"message": "Message sent successfully"}), 200
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500



def save_contact_to_file(name, email, subject, message):
    """Save contact form submission to a JSON file"""
    try:
        data = {
            "name": name,
            "email": email,
            "subject": subject,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        
        # Create contacts.json if it doesn't exist
        try:
            with open('contacts.json', 'r') as f:
                contacts = json.load(f)
        except FileNotFoundError:
            contacts = []
        
        contacts.append(data)
        
        with open('contacts.json', 'w') as f:
            json.dump(contacts, f, indent=2)
            
        print(f"Contact saved to file: {name}")
        return True
        
    except Exception as e:
        print(f"Failed to save contact: {str(e)}")
        return False
    
def send_thankyou_email(name, email):
    """
    Send thank you email to the user
    """
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = email
        msg['Subject'] = "Thank you for contacting me!"
        
        body = f"""
        Hi {name},
        
        Thank you for reaching out to me. I have received your message and will get back to you as soon as possible.
        
        Best regards,
        Kandimalla Sai Kiran
        UI/UX Designer & Frontend Developer
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(EMAIL_USER, email, text)
        server.quit()
        
        print(f"Thank you email sent to {email}")
        
    except Exception as e:
        print(f"Failed to send thank you email: {str(e)}")
        raise

if __name__ == '__main__':
    app.run(debug=True)