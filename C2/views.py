from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import JsonResponse
from django.utils.timezone import now
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import (
    CustomUser, UserEvents, Category, MRNews, UpcomingEvent, EventPost,
    GalleryItem, Highlight, Leader, ImpNews, EventApplication, Institution, Department
)
from .forms import UserEventForm
import random

# Custom Login Required Decorator
def custom_login_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('/login/')
        return view_func(request, *args, **kwargs)
    return wrapper

# Utility Views
def your_view(request):
    response = render(request, "C2/index.html")
    response["ngrok-skip-browser-warning"] = "true"
    return response

def password_reset_complete(request):
    return render(request, "password_reset_complete.html")

# Authentication Views
def user_login(request):
    if request.method == "POST":
        email = request.POST.get("email").lower()  # Convert email to lowercase
        password = request.POST.get("password")

        # Validate email domain
        if not email.endswith('@manavrachna.net'):
            messages.error(request, "Please use your valid Manav Rachna Email")
            return render(request, "C2/login.html")

        try:
            # Convert stored email to lowercase for comparison
            user = CustomUser.objects.get(email__iexact=email)
            user = authenticate(request, username=user.email, password=password)

            if user:
                login(request, user)
                return redirect("index")
            else:
                messages.error(request, "Invalid email or password")
        except CustomUser.DoesNotExist:
            messages.error(request, "Invalid email or password")

    return render(request, "C2/login.html")

def logout_view(request):
    logout(request)
    messages.success(request, "Signin & Start the Buzz!!")
    return redirect("index")

def signup(request):
    institutions = Institution.objects.all()
    
    if request.method == "POST":
        name = request.POST.get("name")
        phone = request.POST.get("phone")
        email = request.POST.get("email")
        password = request.POST.get("password")
        institution_id = request.POST.get("institution")
        department_id = request.POST.get("department")

        # Validate email domain
        if not email.endswith('@manavrachna.net'):
            messages.error(request, "Please use a valid Manav Rachna email (e.g., name@manavrachna.net)")
            return render(request, "C2/signup.html", {"institutions": institutions})

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "An account with this email already exists.")
        elif CustomUser.objects.filter(phone=phone).exists():
            messages.error(request, "An account with this phone number already exists.")
        else:
            # Generate OTP
            otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])

            # Create unverified user
            user = CustomUser.objects.create_user(
                email=email,
                password=password,
                phone=phone,
                institution_id=institution_id,
                department_id=department_id,
                otp=otp,
                is_verified=False
            )
            user.first_name = name
            user.save()

            # Send OTP email
            subject = "Verify Your CampusConnect Account"
            message = f"""
            <html>
                <body style="font-family: Arial, sans-serif;">
                    <h2>Hello {name},</h2>
                    <p>Welcome to CampXConnect! Please use the following OTP to verify your account:</p>
                    <h3 style="color: #4CAF50;">{otp}</h3>
                    <p>This OTP is valid for 10 minutes.</p>
                    <p>Enter this code at: <a href='http://yourdomain.com/verify/'>Verify Now</a></p>
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

            messages.success(request, "Please check your email for OTP verification.")
            return redirect("verify_otp", user_id=user.id)

    return render(request, "C2/signup.html", {"institutions": institutions})

def verify_otp(request, user_id):
    try:
        user = CustomUser.objects.get(id=user_id)
        
        if request.method == "POST":
            entered_otp = request.POST.get("otp")
            
            if user.otp == entered_otp:
                user.is_verified = True
                user.otp = None
                user.save()
                messages.success(request, "Account verified successfully! Please login.")
                return redirect("login")
            else:
                messages.error(request, "Invalid OTP. Please try again.")
        
        return render(request, "C2/verify_otp.html", {"user_id": user_id})
    
    except CustomUser.DoesNotExist:
        messages.error(request, "Invalid verification link.")
        return redirect("signup")

def forgot_password(request):
    if request.method == "POST":
        identifier = request.POST.get("identifier").strip().lower()

        try:
            if "@" in identifier:
                if not identifier.endswith('@manavrachna.net'):
                    return render(request, "forgot_password.html", {"error": "Please use a valid Manav Rachna email"})
                user = CustomUser.objects.get(email=identifier)
            else:
                return render(request, "forgot_password.html", {"error": "Please enter a valid email"})

            email = user.email
            reset_link = request.build_absolute_uri(reverse("reset_password", kwargs={"user_id": user.id}))

            email_context = {
                "username": user.username,
                "reset_link": reset_link,
            }
            html_message = render_to_string("password_reset_email.html", email_context)
            plain_message = strip_tags(html_message)

            send_mail(
                "🔒 Reset Your CampusConnect Password",
                plain_message,
                "admin@campusconnect.com",
                [email],
                fail_silently=False,
                html_message=html_message,
            )

            return render(request, "password_reset_done.html")

        except CustomUser.DoesNotExist:
            return render(request, "forgot_password.html", {"error": "No account found with this email"})

    return render(request, "forgot_password.html")

def reset_password(request, user_id):
    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        return render(request, "reset_password.html", {"error": "Invalid reset link"})

    if request.method == "POST":
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        if new_password != confirm_password:
            return render(request, "reset_password.html", {"error": "Passwords do not match"})

        user.password = make_password(new_password)
        user.save()

        return redirect("password_reset_complete")

    return render(request, "reset_password.html")

# AJAX view to get departments for an institution
def get_departments(request, institution_id):
    try:
        departments = Department.objects.filter(institution_id=institution_id).values('id', 'name')
        return JsonResponse({'departments': list(departments)})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

# Event Hosting
@login_required
def host_event(request):
    if request.method == "POST":
        form = UserEventForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            event = form.save(commit=False)
            event.user = request.user
            
            # Always use the user's actual information for these fields
            event.host_name = request.user.first_name
            event.host_email = request.user.email
            event.host_phone = request.user.phone
            
            # Set department based on user type
            if not request.user.is_superuser:
                event.department = request.user.department
            else:
                event.department = form.cleaned_data['department']
                
            event.save()

            try:
                admin_email = settings.ADMIN_EMAIL
                send_mail(
                    subject="New Event Submission",
                    message=f"A new event has been submitted:\n\n"
                            f"Title: {event.title}\n"
                            f"Description: {event.description}\n"
                            f"Venue: {event.venue}\n"
                            f"Date: {event.date}\n"
                            f"Time: {event.time}\n"
                            f"Image: {event.image}\n"
                            f"Category: {event.category}\n"
                            f"Department: {event.department}\n"
                            f"Apply Link: {event.apply_link}\n"
                            f"Host: {event.host_name}, {event.host_email}, {event.host_phone}",
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[admin_email]
                )
                messages.success(request, "Successfully sent to admin!")
            except Exception as e:
                messages.error(request, "Sorry, but we can't connect now.")

            return redirect(reverse('profile', args=[request.user.email]))
    else:
        # Create form with user instance
        form = UserEventForm(user=request.user)
    
    return render(request, 'C2/host_event.html', {'form': form, 'user': request.user})

# Profile View
@custom_login_required
def profile_view(request, email):
    user = get_object_or_404(CustomUser, email=email)

    upcoming_events = UpcomingEvent.objects.filter(email=user.email, approved=True)
    posts = EventPost.objects.all().order_by('-id')
    user_posts = EventPost.objects.filter(user=user).order_by('-created_at')

    if request.method == "POST":
        event_id = request.POST.get("event_id")
        event_image = request.FILES.get("event_image")
        caption = request.POST.get("caption")

        event = get_object_or_404(UpcomingEvent, id=event_id) if event_id else None

        if event and event_image and caption:
            EventPost.objects.create(
                user=user,
                image=event_image,
                caption=caption
            )
            return redirect("profile", email=email)

    context = {
        "user": user,
        "upcoming_events": upcoming_events,
        "posts": posts,
        "user_posts": user_posts,
    }
    return render(request, "C2/profile.html", context)

@login_required
def delete_post(request, post_id):
    post = get_object_or_404(EventPost, id=post_id)

    if request.user == post.user:
        post.delete()
    
    return redirect("profile", email=request.user.email)

@login_required
def post_event(request):
    if request.method == "POST":
        event_title = request.POST.get("event_title")
        caption = request.POST.get("caption")
        image = request.FILES.get("image")

        post = EventPost(user=request.user, event_title=event_title, caption=caption)
        if image:
            post.image = image
        post.save()

        messages.success(request, "Event posted successfully!")
        return redirect("profile", email=request.user.email)

    return render(request, "profile.html")

from datetime import datetime

def index(request):
    today = datetime.today().date()

    upcoming_events = UpcomingEvent.objects.filter(
        approved=True,
        date__gte=today
    ).order_by('date')

    impnews_list = ImpNews.objects.filter(expiry_date__gte=now().date()).order_by('-id')

    context = {
        "total_users": CustomUser.objects.count(),
        "total_hosting_requests": UserEvents.objects.count(),
        "total_category": Category.objects.count(),
        "mrnews_list": MRNews.objects.all(),
        "upcoming_events": upcoming_events,
        "posts": EventPost.objects.all().order_by('-id'),
        "gallery_items": GalleryItem.objects.all()[:6],
        "highlights": Highlight.objects.all()[:4],
        "leaders": Leader.objects.all()[:6],
        "impnews_list": impnews_list,
    }

    return render(request, "index.html", context)

from django.shortcuts import render
from datetime import datetime, timedelta
from .models import Category, UpcomingEvent, Institution
import logging

# Set up logging
logger = logging.getLogger(__name__)

def upcoming(request):
    categories = Category.objects.all()
    upcoming_events = UpcomingEvent.objects.filter(approved=True)
    institutions = Institution.objects.all()
    
    # Debug: Log event dates to check their values
    today = datetime.now().date()
    logger.info(f"Today's date: {today}")
    for event in upcoming_events:
        event_date = event.date
        adjusted_date = event_date + timedelta(days=1) if event_date else None
        is_past = adjusted_date < today if adjusted_date else False
        logger.info(f"Event: {event.title}, Date: {event_date}, Adjusted Date: {adjusted_date}, Is Past: {is_past}")

    context = {
        'upcoming_events': upcoming_events,
        'categories': categories,
        'institutions': institutions,
        'today': today,
    }
    return render(request, 'C2/upcoming.html', context)
    
@custom_login_required
def feed(request):
    event_posts = EventPost.objects.all().order_by("-created_at")
    context = {"event_posts": event_posts}
    return render(request, "C2/feed.html", context)

@custom_login_required
def post_detail(request, post_id):
    post = get_object_or_404(EventPost, id=post_id)
    return render(request, "C2/post_detail.html", {"post": post})