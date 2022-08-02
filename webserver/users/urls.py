from django.conf.urls.static import static
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('register/', views.register, name='register'),  # FIX ME
    path('profile/', views.profile, name='profile'),  # FIX ME
    path('login/', auth_views.LoginView.as_view(template_name="users/login.html"), name='login'),
    path('logout/', views.logout, name='logout'),  # FIX ME
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="users/password_reset_confirm.html"), name='password_reset_confirm'),  # FIX ME
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name="users/password_reset.html"), name='password_reset'),  # FIX ME
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name="users/password_reset_done.html"), name='password_reset_done'),  # FIX ME
    path('password-reset/complete/', auth_views.PasswordResetCompleteView.as_view(template_name="users/password_reset_complete.html"), name='password_reset_complete')  # FIX ME
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
