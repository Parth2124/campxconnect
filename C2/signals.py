print("✅ Signals module loaded!")  # Debugging statement

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.utils.html import format_html
from .models import UpcomingEvent, MRNews, CustomUser  # ✅ Import MRNews

def send_html_email(subject, message, recipients):
    """Helper function to send an HTML email"""
    send_mail(
        subject,
        "",
        settings.DEFAULT_FROM_EMAIL,
        recipients,
        html_message=message,  # HTML content
        fail_silently=False,
    )

# ✅ Email Notification for MREvents
# @receiver(post_save, sender=MREvents)
# def notify_users_mrevents(sender, instance, created, **kwargs):
#     print(f"MR-Event Signal Triggered: {instance.title}")  # Debugging
    
#     subject = f"📰 {'New' if created else 'Updated'} MR-Event: {instance.title}"
    
#     message = format_html(
#         """
#         <div style="font-family: Arial, sans-serif; padding: 20px; border: 1px solid #ddd; border-radius: 10px; max-width: 600px;">
#             <h2 style="color: #0056b3;">{}</h2>
#             <p style="font-size: 16px; color: #333;">{}</p>
#             <hr style="border: 1px solid #ddd;">
#             <p><strong>Date:</strong> {}</p>
#             <p><strong>Venue:</strong> {}</p>
#             <p><strong>Contact:</strong> {}</p>
#             <a href="https://2987-2405-201-4042-a05b-88d0-9d6f-495c-1ed9.ngrok-free.app/" style="display: inline-block; padding: 10px 15px; color: white; background-color: #28a745; text-decoration: none; border-radius: 5px;">Read More</a>
#             <hr style="border: 1px solid #ddd;">
#             <p style="text-align: center; font-size: 14px; color: #666;">
#                 <strong>CampusConnect</strong> | Stay Updated, Stay Connected 🚀
#             </p>
#         </div>
#         """,
#         instance.title,
#         instance.description,
#         instance.date if instance.date else "N/A",
#         instance.venue if instance.venue else "N/A",
#         instance.contact_number if instance.contact_number else "N/A",
#     )

#     recipients = list(CustomUser.objects.values_list('email', flat=True))

#     if recipients:
#         print(f"Sending email to: {recipients}")  # Debugging
#         send_html_email(subject, message, recipients)

# ✅ Email Notification for Events
@receiver(post_save, sender=UpcomingEvent)
def notify_users_event(sender, instance, created, **kwargs):
    print(f"Event Signal Triggered: {instance.title}")  # Debugging
    
    subject = f"🎉 {'New' if created else 'Updated'} Event: {instance.title}"
    
    message = format_html(
        """
        <div style="font-family: Arial, sans-serif; padding: 20px; border: 1px solid #ddd; border-radius: 10px; max-width: 600px;">
            <h2 style="color: #e83e8c;">{}</h2>
            <p style="font-size: 16px; color: #333;">{}</p>
            <hr style="border: 1px solid #ddd;">
            <p><strong>Date:</strong> {}</p>
            <p><strong>Venue:</strong> {}</p>
            <p><strong>Contact:</strong> {}</p>
            <a href="https://2987-2405-201-4042-a05b-88d0-9d6f-495c-1ed9.ngrok-free.app/" style="display: inline-block; padding: 10px 15px; color: white; background-color: #e83e8c; text-decoration: none; border-radius: 5px;">Read More</a>
            <hr style="border: 1px solid #ddd;">
            <p style="text-align: center; font-size: 14px; color: #666;">
                <strong>CampusConnect</strong> | Stay Updated, Stay Connected 🚀
            </p>
        </div>
        """,
        instance.title,
        instance.description,
        instance.date if instance.date else "N/A",
        instance.venue if instance.venue else "N/A",
        instance.contact_number if hasattr(instance, 'contact_number') and instance.contact_number else "N/A",
    )

    recipients = list(CustomUser.objects.values_list('email', flat=True))

    if recipients:
        print(f"Sending email to: {recipients}")  # Debugging
        send_html_email(subject, message, recipients)

# ✅ Email Notification for MRNews
@receiver(post_save, sender=MRNews)
def notify_users_mrnews(sender, instance, created, **kwargs):
    print(f"MR-News Signal Triggered: {instance.title}")  # Debugging
    
    subject = f"📰 {'New' if created else 'Updated'} MR-News: {instance.title}"
    
    message = format_html(
        """
        <div style="font-family: Arial, sans-serif; padding: 20px; border: 1px solid #ddd; border-radius: 10px; max-width: 600px;">
            <h2 style="color: #ff9800;">{}</h2>
            <p style="font-size: 16px; color: #333;">{}</p>
            <hr style="border: 1px solid #ddd;">
            <p><strong>Published On:</strong> {}</p>
            <p><strong>By:</strong> {}</p>
            <a href="https://2987-2405-201-4042-a05b-88d0-9d6f-495c-1ed9.ngrok-free.app/" style="display: inline-block; padding: 10px 15px; color: white; background-color: #ff5722; text-decoration: none; border-radius: 5px;">Read More</a>
            <hr style="border: 1px solid #ddd;">
            <p style="text-align: center; font-size: 14px; color: #666;">
                <strong>CampusConnect</strong> | Stay Updated, Stay Connected 🚀
            </p>
        </div>
        """,
        instance.title,
        instance.description,
        instance.created_at.strftime("%d %B %Y") if instance.created_at else "N/A",
        instance.by if instance.by else "Unknown",
    )

    recipients = list(CustomUser.objects.values_list('email', flat=True))

    if recipients:
        print(f"Sending email to: {recipients}")  # Debugging
        send_html_email(subject, message, recipients)
