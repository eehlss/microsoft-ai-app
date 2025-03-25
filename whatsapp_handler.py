import os
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from flask import Flask, request
from rag_chatbot import get_chatbot_response
import re

# Initialize Twilio client
try:
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    if not account_sid or not auth_token:
        raise ValueError("Twilio credentials not found")
    if not account_sid.startswith('AC'):
        raise ValueError("Invalid Account SID format - should start with 'AC'")

    client = Client(account_sid, auth_token)
    print("Successfully initialized Twilio client")
except Exception as e:
    print(f"Error initializing Twilio client: {str(e)}")

# Initialize Flask app for webhook
app = Flask(__name__)

# Store doctor's number
DOCTOR_NUMBER = "+2347037819697"

def validate_phone_number(phone_number):
    """Validate phone number format"""
    # Remove any whitespace and check basic format
    phone_number = phone_number.strip()
    if not phone_number.startswith('+'):
        phone_number = '+' + phone_number

    # Check if it's a valid phone number format
    pattern = re.compile(r'^\+\d{10,15}$')
    if not pattern.match(phone_number):
        raise ValueError("Invalid phone number format. Must start with + and contain 10-15 digits")

    return phone_number

def format_whatsapp_number(phone_number):
    """Format phone number for WhatsApp"""
    try:
        # Remove any existing formatting
        phone_number = phone_number.replace('whatsapp:', '')
        phone_number = phone_number.strip()

        # Validate basic format
        if not phone_number.startswith('+'):
            phone_number = '+' + phone_number

        # Format for WhatsApp Sandbox/Business API
        formatted_number = f"whatsapp:{phone_number}"
        print(f"Formatted WhatsApp number: {formatted_number}")
        return formatted_number
    except Exception as e:
        print(f"Error formatting WhatsApp number: {str(e)}")
        raise ValueError("Invalid WhatsApp number format")

def send_whatsapp_message(to_number, message):
    """Send a WhatsApp message using Twilio"""
    try:
        # Validate phone number
        to_number = validate_phone_number(to_number)
        print(f"Attempting to send WhatsApp message to {to_number}")

        # Get Twilio number
        from_number = os.getenv('TWILIO_PHONE_NUMBER')
        if not from_number:
            raise ValueError("Twilio phone number not configured")

        # Validate Twilio number format
        from_number = validate_phone_number(from_number)
        print(f"Using Twilio number: {from_number}")

        # Format numbers for WhatsApp
        from_whatsapp = format_whatsapp_number(from_number)
        to_whatsapp = format_whatsapp_number(to_number)

        print(f"Sending message from {from_whatsapp} to {to_whatsapp}")

        # Send message
        try:
            message = client.messages.create(
                from_=from_whatsapp,
                body=message,
                to=to_whatsapp
            )
            print(f"Successfully sent message with SID: {message.sid}")
            return True
        except Exception as e:
            if "63007" in str(e):
                print("Error: WhatsApp channel not found. Please ensure the Twilio number is configured for WhatsApp in the Twilio Console")
                return False
            elif "21211" in str(e):
                print("Error: Invalid phone number format or not connected to sandbox")
                return False
            elif "21608" in str(e):
                print("Error: Number not connected to WhatsApp sandbox")
                return False
            raise e

    except ValueError as e:
        print(f"Validation error: {str(e)}")
        return False
    except Exception as e:
        print(f"Error sending WhatsApp message: {str(e)}")
        return False

@app.route("/whatsapp", methods=['POST'])
def whatsapp_webhook():
    """Handle incoming WhatsApp messages"""
    try:
        print("Received WhatsApp webhook request")
        # Get incoming message details
        incoming_msg = request.values.get('Body', '')
        sender_number = request.values.get('From', '')

        # Remove WhatsApp prefix if present
        sender_number = sender_number.replace('whatsapp:', '')
        print(f"Message from {sender_number}: {incoming_msg}")

        # Initialize response
        resp = MessagingResponse()

        # Check if message starts with "doctor:" to forward to doctor
        if incoming_msg.lower().startswith("doctor:"):
            try:
                # Forward message to doctor
                message_to_doctor = f"Patient ({sender_number}): {incoming_msg[7:]}"
                if send_whatsapp_message(DOCTOR_NUMBER, message_to_doctor):
                    resp.message("Message forwarded to doctor. They will respond soon.")
                else:
                    resp.message("Sorry, couldn't forward your message to the doctor. Please try again later.")
            except Exception as e:
                print(f"Error forwarding message to doctor: {str(e)}")
                resp.message("Error forwarding message. Please try again later.")

        # Check if it's the doctor responding (from their registered number)
        elif sender_number == DOCTOR_NUMBER and ":" in incoming_msg:
            try:
                patient_number, message = incoming_msg.split(":", 1)
                patient_number = validate_phone_number(patient_number.strip())
                message = message.strip()

                if send_whatsapp_message(patient_number, f"Doctor: {message}"):
                    resp.message("Response sent to patient.")
                else:
                    resp.message("Failed to send response to patient.")
            except ValueError as e:
                print(f"Invalid phone number format: {str(e)}")
                resp.message("Invalid phone number format. Please use format: +1234567890: your message")
            except Exception as e:
                print(f"Error processing doctor's response: {str(e)}")
                resp.message("Error sending response. Please try again with format: patient_number: your message")

        # Otherwise, use chatbot
        else:
            try:
                print("Getting chatbot response")
                chatbot_response = get_chatbot_response(incoming_msg)
                resp.message(chatbot_response)
                print("Successfully sent chatbot response")
            except Exception as e:
                print(f"Error getting chatbot response: {str(e)}")
                resp.message("I'm sorry, I couldn't process your request. Please try again later.")

        return str(resp)

    except Exception as e:
        print(f"Error in webhook: {str(e)}")
        return str(MessagingResponse().message("An error occurred. Please try again later."))

if __name__ == "__main__":
    # Only run the Flask app when deployed separately (e.g., on Azure)
    if os.getenv('DEPLOY_WHATSAPP_SERVER', 'false').lower() == 'true':
        app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))