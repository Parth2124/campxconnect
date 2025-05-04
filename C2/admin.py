from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.core.mail import send_mail
from django.conf import settings
from django.utils.timezone import now
from django.contrib import messages
from datetime import timedelta
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from import_export.formats.base_formats import XLSX
from .models import (
    CustomUser, UpcomingEvent, MRNews, EventApplication, Category, UserEvents,
    GalleryItem, Highlight, Leader, ImpNews, EventPost, Institution, Department
)

# Register Existing Models
admin.site.register(GalleryItem)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(UserEvents)
class UserEventsAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'user', 'host_email']
    actions = ['approve_events', 'reject_events']

    @admin.action(description="Approve selected events")
    def approve_events(self, request, queryset):
        for event in queryset:
            if event.status != 'Approved':
                event.status = 'Approved'
                event.save()

            now_date = now().date()
            common_fields = {
                'title': event.title,
                'description': event.description,
                'date': event.date,
                'venue': event.venue,
                'image': event.image,
                'category': event.category,
                'host': event.user,
                'link': event.apply_link,
                'time': event.time,
                'contact_number': event.host_phone,
                'email': event.host_email,
                'approved': True,
                'institution': event.user.institution
            }

            UpcomingEvent.objects.create(**common_fields)

            try:
                user_email = event.user.email
                email_content = f"""
                <html>
                <body style="font-family: Arial, sans-serif; color: #333;">
                    <p>Dear {event.user.username},</p>
                    <p>Your event <strong style="color: green;">'{event.title}'</strong> has been <strong>Approved!</strong> 🎉</p>
                    <p>Check it out on CampusConnect.</p>
                    <p>Regards,<br>CampusConnect Team</p>
                </body>
                </html>
                """
                send_mail(
                    subject="Event Approved 🎉",
                    message="This is an HTML email. Please enable HTML view.",
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[user_email],
                    html_message=email_content,
                    fail_silently=False
                )
                messages.success(request, f"Event '{event.title}' approved and email sent.")
            except Exception as e:
                messages.error(request, f"Failed to send email for '{event.title}'. Error: {str(e)}")

    @admin.action(description="Reject selected events")
    def reject_events(self, request, queryset):
        for event in queryset:
            if event.status != 'Rejected':
                event.status = 'Rejected'
                event.save()

                try:
                    user_email = event.user.email
                    expiration_date = (now() + timedelta(days=2)).strftime("%d-%m-%Y")
                    email_content = f"""
                    <html>
                    <body style="font-family: Arial, sans-serif; color: #333;">
                        <p>Dear {event.user.username},</p>
                        <p>Your event <strong style="color: red;">'{event.title}'</strong> has been <strong>Rejected</strong>.</p>
                        <p>Contact us within <strong>2 days</strong> (before <strong>{expiration_date}</strong>) at:</p>
                        <p><strong>Email:</strong> <a href="mailto:cx.campusconnect@gmail.com" style="color: #1E88E5;">cx.campusconnect@gmail.com</a></p>
                        <p>Regards,<br>CampusConnect Team</p>
                    </body>
                    </html>
                    """
                    send_mail(
                        subject="Event Rejected ❌",
                        message="This is an HTML email. Please enable HTML view.",
                        from_email=settings.EMAIL_HOST_USER,
                        recipient_list=[user_email],
                        html_message=email_content,
                        fail_silently=False
                    )
                    messages.success(request, f"Event '{event.title}' rejected and email sent.")
                except Exception as e:
                    messages.error(request, f"Failed to send rejection email for '{event.title}'. Error: {str(e)}")

# Custom User Admin
class CustomUserResource(resources.ModelResource):
    class Meta:
        model = CustomUser
        fields = ('first_name', 'email', 'phone', 'institution', 'department')

    def before_import_row(self, row, **kwargs):
        email = row.get('email')
        if not email.endswith('@manavrachna.net'):
            raise ValueError("Invalid email domain. Must be @manavrachna.net")

        institution_name = row.get('institution')
        department_name = row.get('department')

        if institution_name:
            institution, _ = Institution.objects.get_or_create(name=institution_name)
            row['institution'] = institution.id
        if department_name and institution_name:
            department, _ = Department.objects.get_or_create(
                institution=institution,
                name=department_name
            )
            row['department'] = department.id

        user = CustomUser.objects.filter(email=email).first()
        if user:
            user.first_name = row.get('first_name')
            user.phone = row.get('phone')
            user.institution_id = row.get('institution')
            user.department_id = row.get('department')
            user.save()
        else:
            user = CustomUser(
                email=email,
                first_name=row.get('first_name'),
                phone=row.get('phone'),
                institution_id=row.get('institution'),
                department_id=row.get('department'),
            )
            user.set_password(row.get('phone'))
            user.save()

            try:
                subject = "🎉 Welcome to CampusConnect!"
                message = f"""
                <html>
                    <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
                        <div style="max-width: 600px; background: #ffffff; padding: 20px; border-radius: 8px; box-shadow: 0px 4px 8px rgba(0,0,0,0.2);">
                            <h2 style="color: #333;">Hello, {row.get('first_name')}! 👋</h2>
                            <p style="color: #555;">Welcome to <strong>CampusConnect</strong>. We’re excited to have you on board.</p>
                            <p style="color: #555;">Here are your login details:</p>
                            <div style="background: #f0f0f0; padding: 10px; border-radius: 5px;">
                                <p><strong>Email:</strong> {email}</p>
                                <p><strong>Password:</strong> {row.get('phone')} (Your phone number)</p>
                            </div>
                            <p style="color: #555;">You can now log in and start exploring!</p>
                            <a href="https://yourdomain.com/login/" style="display: inline-block; background: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; font-size: 16px;">Login Now</a>
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
                    "",
                    settings.EMAIL_HOST_USER,
                    [email],
                    fail_silently=False,
                    html_message=message,
                )
            except Exception as e:
                print(f"Failed to send email to {email}: {str(e)}")
        return row

@admin.register(CustomUser)
class CustomUserAdmin(ImportExportModelAdmin, UserAdmin):
    resource_class = CustomUserResource
    list_display = ("email", "phone", "first_name", "institution", "department", "is_verified", "is_staff", "is_active")
    search_fields = ("email", "phone", "first_name")
    ordering = ("email",)
    list_filter = ("is_verified", "is_staff", "is_active", "institution", "department")
    
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal Info", {"fields": ("first_name", "phone", "institution", "department")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Verification", {"fields": ("is_verified", "otp")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "phone", "first_name", "institution", "department", "password1", "password2"),
        }),
    )
    
    def get_import_formats(self):
        formats = super().get_import_formats()
        formats.append(base_formats.XLSX)
        return formats

@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    list_display = ("name", "code")
    search_fields = ("name", "code")

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "institution")
    search_fields = ("name", "institution__name")
    list_filter = ("institution",)

@admin.register(ImpNews)
class ImpNewsAdmin(admin.ModelAdmin):
    list_display = ("title", "expiry_date", "institution")
    list_filter = ("expiry_date", "institution")
    search_fields = ("title",)

@admin.register(EventPost)
class EventPostAdmin(admin.ModelAdmin):
    list_display = ('event_title', 'user', 'created_at', 'institution')
    search_fields = ('event_title', 'user__username')
    list_filter = ('created_at', 'institution')

@admin.register(UpcomingEvent)
class UpcomingEventAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'date', 'institution')
    list_filter = ('category', 'institution')

@admin.register(MRNews)
class NewsAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "published_date", "institution")
    list_filter = ("category", "institution")
    search_fields = ("title", "description")

@admin.register(EventApplication)
class EventApplicationAdmin(admin.ModelAdmin):
    list_display = ("user", "event_name", "category", "applied_date")
    search_fields = ("user__email", "event_name")

@admin.register(Highlight)
class HighlightAdmin(admin.ModelAdmin):
    list_display = ('title', 'date')
    search_fields = ('title', 'description')

@admin.register(Leader)
class LeaderAdmin(admin.ModelAdmin):
    list_display = ('name', 'position')
    search_fields = ('name', 'position')