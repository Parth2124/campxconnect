# script.py
import pandas as pd
import os
import django
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.hashers import make_password

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campusconnect.settings')
django.setup()

from C2.models import CustomUser

# Read the CSV file
df = pd.read_csv('students.csv')  # Replace with your CSV file name

# Iterate over each row and create a CustomUser object
for index, row in df.iterrows():
    name = row['name']
    email = row['email']
    phone = row['contact_number']
    trn = row['trn']

    # Check if TRN, email, or phone already exists
    if CustomUser.objects.filter(trn=trn).exists():
        print(f"Skipping {trn}: TRN already exists.")
        continue
    if CustomUser.objects.filter(email=email).exists():
        print(f"Skipping {email}: Email already exists.")
        continue
    if CustomUser.objects.filter(phone=phone).exists():
        print(f"Skipping {phone}: Phone number already exists.")
        continue

    try:
        # Create the user
        user = CustomUser.objects.create_user(
            username=trn,
            email=email,
            password=phone,  # Set phone number as password
            phone=phone,
            trn=trn
        )
        user.first_name = name
        user.save()

        # Send welcome email
        subject = "🎉 Welcome to CampusConnect!"
        message = f"""
        <html>
            <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
                <div style="max-width: 600px; background: #ffffff; padding: 20px; border-radius: 8px; box-shadow: 0px 4px 8px rgba(0,0,0,0.2);">
                    <h2 style="color: #333;">Hello, {name}! 👋</h2>
                    <p style="color: #555;">Welcome to <strong>CampusConnect</strong>. We’re excited to have you on board.</p>
                    <p style="color: #555;">Here are your login details:</p>
                    <div style="background: #f0f0f0; padding: 10px; border-radius: 5px;">
                        <p><strong>Username (TRN):</strong> {trn}</p>
                        <p><strong>Email:</strong> {email}</p>
                        <p><strong>Password:</strong> {phone} (Your phone number)</p>
                    </div>
                    <p style="color: #555;">You can now log in and start exploring!</p>
                    <a href="https://2987-2405-201-4042-a05b-88d0-9d6f-495c-1ed9.ngrok-free.app/login/" style="display: inline-block; background: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; font-size: 16px;">Login Now</a>
                    <p style="color: #777; font-size: 12px; margin-top: 20px;">
                        If you have any issues, feel free to contact us.<br>
                        <strong>Admin:</strong> You can reach out at 
                        <a href="mailto:cx.campusconnect@gmail.com" style="color: #007bff; text-decoration: none;">cx.campusconnect@gmail.com</a>
                    </p>
                </div>
            </body>
        </html>
        """
        send_mail(
            subject,
            "",  # Empty string since we are using an HTML message
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
            html_message=message,
        )
        print(f"User {trn} created successfully and email sent.")

    except Exception as e:
        print(f"Error creating user {trn}: {str(e)}")

print("Data import completed!")