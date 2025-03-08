import os
import pytz
import dotenv
import smtplib
import birthday
from datetime import datetime
import google.generativeai as genai
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load environment variables from .env file
dotenv.load_dotenv()

# Configure the generative AI model using API key from environment variables
genai.configure(api_key=os.getenv('API'))
model = genai.GenerativeModel("gemini-2.0-flash-exp")

def get_birthday_message(dob, sender: str):
    """
    Generate a personalized birthday message using generative AI.

    Parameters:
    - dob: Date of birth details used for age calculation.
    - sender: The sender's name to be included in the message.
    """
    # Prepare prompt with required details for message generation
    prompt = f"""
You are a skilled birthday message writer. Your task is to generate a personalized birthday message that is completely self-contained and ready to be sent directly. The message should be warm, heartfelt, and sincere, incorporating the following details:
- Name: Use a placeholder here
- Date of Birth: {dob} (Calculate age from this date. Today's date {datetime.now(pytz.timezone('Asia/Kolkata')).replace(tzinfo=None).strftime("%d-%m-%Y")})
- Relationship: My college college friend

The message should include:
- A greeting with birthday wishes
- Positive wishes for the future or the year ahead
- A friendly, warm, and sincere tone that avoids being too formal
- A heartfelt message that conveys good vibes and genuine celebration

Return Format:
- It should be a text without any subject
- For the final regards part of the message, use {sender} as the name
- The message should be ready to send and there shouldn't be a part to insert/change anything

Please ensure that the final message is personalized based on these details and does not exceed 150 words.
"""

    # Generate birthday message using the AI model
    response = model.generate_content(prompt)
    return response.text

def send_email(sender_name: str, receiver_email: str):
    """
    Compose and send an email containing a birthday notification and personalized wishes.

    Parameters:
    - sender_name: Name to be used in the personalized message.
    - receiver_email: Recipient's email address.
    """
    # Retrieve birthday data and convert it to an HTML table
    df = birthday.get_dataframe()
    if df.empty: return False
    df_html = df.to_html(index=False, classes='birthday-table')

    # Concatenate all DOB entries and generate the birthday message
    dob = ' and '.join(df['DOB'].to_list())
    response_text = get_birthday_message(dob, sender=sender_name)

    # Replace newline characters with HTML line breaks for proper formatting
    message_text = response_text.replace("\n", "<br>")

    # Define the HTML content for the email with inline CSS for styling
    html = f"""
<html>
<head>
    <meta charset="UTF-8">
    <title>Birthday Celebration Notification</title>
    <style>
        /* Keyframe animations */
        @keyframes fadeIn {{
            0% {{ opacity: 0; }}
            100% {{ opacity: 1; }}
        }}
        @keyframes slideIn {{
            0% {{ transform: translateY(-20px); opacity: 0; }}
            100% {{ transform: translateY(0); opacity: 1; }}
        }}
        body {{
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            background: linear-gradient(135deg, #E0EAFC, #CFDEF3);
            margin: 0;
            padding: 20px;
            animation: fadeIn 2s ease-in-out;
        }}
        .container {{
            max-width: 650px;
            margin: auto;
            background: #ffffff;
            border-radius: 10px;
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
            overflow: hidden;
            animation: slideIn 1s ease-out;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: #fff;
            text-align: center;
            padding: 40px 20px;
        }}
        .header h1 {{
            margin: 0;
            font-size: 32px;
            letter-spacing: 1px;
        }}
        .content {{
            padding: 30px;
        }}
        h2 {{
            color: #333;
            font-size: 24px;
            border-bottom: 2px solid #ddd;
            padding-bottom: 5px;
            margin-bottom: 20px;
        }}
        /* Container for the DataFrame table to allow horizontal scrolling */
        .table-container {{
            overflow-x: auto;
            margin-bottom: 30px;
        }}
        .birthday-table {{
            width: 100%;
            border-collapse: collapse;
            min-width: 900px; /* Adjust this value if needed */
        }}
        .birthday-table th, .birthday-table td {{
            border: 1px solid #ccc;
            padding: 12px;
            text-align: center;
            transition: background-color 0.3s ease;
        }}
        .birthday-table th {{
            background-color: #f7f7f7;
            font-weight: bold;
        }}
        .birthday-table tr:nth-child(even) {{
            background-color: #fefefe;
        }}
        .birthday-table tr:hover {{
            background-color: #f1f1f1;
        }}
        .message {{
            background-color: #e8f4fd;
            border-left: 6px solid #3498db;
            padding: 20px;
            border-radius: 5px;
            font-size: 18px;
            line-height: 1.6;
            color: #2c3e50;
            margin-bottom: 30px;
        }}
        .footer {{
            background-color: #f7f7f7;
            text-align: center;
            padding: 20px;
            font-size: 14px;
            color: #777;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Birthday Celebration Notification</h1>
        </div>
        <div class="content">
            <h2>Today's Birthday Celebrations</h2>
            <div class="table-container">
                {df_html}
            </div>
            <h2>Birthday Wishes</h2>
            <div class="message">
                {message_text}
            </div>
        </div>
        <div class="footer">
            &copy; 2025 Birthday Celebrations. Confidential and Proprietary. All rights reserved.<br>
            This email and its contents are intended solely for the designated recipient. If you have received this email in error, please notify the sender immediately and delete it from your system.
        </div>
    </div>
</body>
</html>
"""

    # Retrieve sender credentials from environment variables
    sender_email = os.getenv('SENDER_EMAIL')
    sender_password = os.getenv('EMAIL_PASSWORD')

    # Set up the email message with MIME structure
    msg = MIMEMultipart('alternative')
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = "Birthday Finder Notification"

    msg.attach(MIMEText(html, 'html'))

    try:
        # Connect to Gmail's SMTP server, login, and send the email
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
    except Exception as e:
        # Print error message if email sending fails
        print(f"Error: {e}")
        return False

    return True
