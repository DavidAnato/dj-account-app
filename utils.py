from django.core.mail import EmailMultiAlternatives, send_mail
from django.utils.html import strip_tags
from django.conf import settings


def send_password_reset_email(email, reset_link):
    subject = 'Password Reset Request'
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Password Reset Request</title>
        <style>
            body {{
                background-color: #f3f4f6;
                font-family: Arial, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                marging: 0 auto;
            }}
            .container {{
                max-width: 600px;
                padding: 20px;
                background-color: #ffffff;
                border: 1px solid #ccc;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                text-align: center;
            }}
            .btn {{
                display: inline-block;
                padding: 10px 20px;
                background-color: #007bff;
                color: #fff;
                text-decoration: none;
                border-radius: 3px;
                margin-top: 20px;
                font-size: 1.2rem;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2 style="font-size: 1.5rem; font-weight: 600; margin-bottom: 1rem;">Password Reset Request</h2>
            <p>Hello,</p>
            <p>We received a request to reset your password. Click the button below to proceed:</p>
            <a href="{reset_link}" class="btn">Reset Password</a>
            <p style="margin-top: 20px;">If you did not request this, you can safely ignore this email.</p>
            <p>Regards,<br>The X-TECH Team</p>
        </div>
    </body>
    </html>
    """
    text_content = strip_tags(html_content)  # Strip the HTML tags to get the text version
    email = EmailMultiAlternatives(subject, text_content, from_email=settings.EMAIL_HOST_USER, to=[email])
    email.attach_alternative(html_content, "text/html")
    email.send()

def send_activation_email(email, otp_code, activation_link):
    subject = 'Activate Your Account'
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Activate Your Account</title>
        <style>
            body {{
                background-color: #f3f4f6;
                font-family: Arial, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
            }}
            .container {{
                max-width: 600px;
                padding: 20px;
                background-color: #ffffff;
                border: 1px solid #ccc;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                text-align: center;
                marging: 0 auto;
            }}
            .btn {{
                display: inline-block;
                padding: 10px 20px;
                background-color: #007bff;
                color: #fff;
                text-decoration: none;
                border-radius: 3px;
                margin-top: 20px;
                font-size: 1.2rem;

            }}
            .otp-code {{
                font-size: 2rem;
                font-weight: 600;
                margin-top: 1.3rem;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2 style="font-size: 1.5rem; font-weight: 600; margin-bottom: 1rem;">Activate Your Account</h2>
            <p>Hello,</p>
            <p>Thank you for registering with X-TECH. Your OTP for account activation is:</p>
            <p class="otp-code">{otp_code}</p>
            <hr style="margin: 20px 0;">
            or
            <hr style="margin: 20px 0;">
            <a href="{activation_link}" class="btn">Activate Account</a>
            <p style="margin-top: 20px;">This OTP is valid for 3 hours.</p>
            <p>Regards,<br>The X-TECH Team</p>
        </div>
    </body>
    </html>
    """
    text_content = strip_tags(html_content)  # Strip the HTML tags to get the text version
    email = EmailMultiAlternatives(subject, text_content, from_email=settings.EMAIL_HOST_USER, to=[email])
    email.attach_alternative(html_content, "text/html")
    email.send()
