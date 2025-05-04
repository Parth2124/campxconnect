from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.conf import settings
from django.utils.timezone import now
from django.core.validators import RegexValidator
from datetime import timedelta
from django.urls import reverse

class CustomUserManager(BaseUserManager):
    def create_user(self, email, phone, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        if not phone:
            raise ValueError("The Phone field must be set")
        if not email.endswith('@manavrachna.net'):
            raise ValueError("Email must be a valid Manav Rachna email (e.g., name@manavrachna.net)")
        email = self.normalize_email(email)
        user = self.model(email=email, username=email, phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_verified', True)  # Superusers are verified by default
        extra_fields.setdefault('institution', None)  # Allow null for superuser
        extra_fields.setdefault('department', None)   # Allow null for superuser

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, phone, password, **extra_fields)

class Institution(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    
    def __str__(self):
        return self.name

class Department(models.Model):
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='departments')
    name = models.CharField(max_length=100)
    
    class Meta:
        unique_together = ('institution', 'name')
    
    def __str__(self):
        return f"{self.name} ({self.institution.name})"

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, unique=True)
    institution = models.ForeignKey(Institution, on_delete=models.SET_NULL, null=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    is_verified = models.BooleanField(default=False)
    otp = models.CharField(max_length=6, null=True, blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["phone"]

    groups = models.ManyToManyField(
        "auth.Group",
        related_name="customuser_set",
        blank=True,
        verbose_name="groups",
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="customuser_set",
        blank=True,
        verbose_name="user permissions",
    )

    def save(self, *args, **kwargs):
        self.username = self.email
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} ({self.email})"

    @property
    def code(self):
        return self.institution.code if self.institution else None

# ... (other models like Category, UserEvents, etc., remain unchanged)

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "categories"

class UserEvents(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    venue = models.CharField(max_length=255)
    date = models.DateField()
    time = models.TimeField()
    image = models.ImageField(upload_to="event_images/", null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    apply_link = models.URLField()
    host_name = models.CharField(max_length=255)
    host_email = models.EmailField()
    host_phone = models.CharField(max_length=15)
    status = models.CharField(
        max_length=10,
        choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')],
        default='Pending'
    )

    def __str__(self):
        return self.title

class Spotlight(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='spotlights/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class GalleryItem(models.Model):
    image = models.ImageField(upload_to='gallery/')
    caption = models.CharField(max_length=200)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.caption

class Highlight(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateField()
    image = models.ImageField(upload_to='highlights/', blank=True, null=True)

    def __str__(self):
        return self.title

class Leader(models.Model):
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    image = models.ImageField(upload_to='leaders/', blank=True, null=True)

    def __str__(self):
        return self.name

class UpcomingEvent(models.Model):
    title = models.CharField(max_length=255, null=False, blank=True)
    description = models.TextField()
    date = models.DateField()
    venue = models.CharField(max_length=255, null=True, blank=True)
    image = models.ImageField(upload_to="event_images/", null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    host = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    link = models.URLField(blank=True, null=True)
    time = models.TimeField(null=True, blank=True)
    contact_number = models.CharField(max_length=15, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    approved = models.BooleanField(default=False)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.title

class EventPost(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    event_title = models.CharField(max_length=255, null=False, blank=True)
    caption = models.TextField()
    image = models.ImageField(upload_to="event_images/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.event_title}"
    
    def get_absolute_url(self):
        return reverse('post_detail', args=[str(self.id)])

class ImpNews(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    expiry_date = models.DateField()
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.title

def get_expiry_date():
    return now() + timedelta(days=7)

class MRNews(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to="mrnews_images/", default="/mrnews_images/MRIIRS1.png")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    published_date = models.DateTimeField(auto_now_add=True, null=True)
    by = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(default=now)
    expiry_date = models.DateTimeField(default=get_expiry_date)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.title

class EventApplication(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    event_name = models.CharField(max_length=200)
    category = models.CharField(max_length=100)
    applied_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.event_name}"