from django.conf import settings
from django.urls import path
from . import views
from django.conf.urls.static import static

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.user_login, name="login"),
    path("signup/", views.signup, name="signup"),
    path("logout/", views.logout_view, name="logout"),
    path("reset-password/<int:user_id>/", views.reset_password, name="reset_password"),
    path("password-reset-complete/", views.password_reset_complete, name="password_reset_complete"),
    path("feed/", views.feed, name="feed"),
    path("post-event/", views.post_event, name="post_event"),
    path("delete-post/<int:post_id>/", views.delete_post, name="delete-post"),
    path('forgot-password/', views.forgot_password, name='forgot-password'),
    path('profile/<str:email>/', views.profile_view, name='profile'),
    path('host-event/', views.host_event, name='host_event'),
    path("upcoming/", views.upcoming, name="upcoming"),
    path("verify/<int:user_id>/", views.verify_otp, name="verify_otp"),
    path("post/<int:post_id>/", views.post_detail, name="post_detail"),
    path('get_departments/<int:institution_id>/', views.get_departments, name='get_departments'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)