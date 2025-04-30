# Django Login OTP via Email

This quick project adds a simple login One Time Password to your Django project.  By default, users without email addresses are simply logged in.

## Installation instructions

- Check out repository in folder named 'django_login_otp'
- Add 'django_login_otp' to your INSTALLED_APPS in settings.py
- python manage.py migrate
- Customize the 2 templates:
  - email_code.html is the text that will be sent to your users
  - enter_otp.html is the screen they use to enter the One Time Password
- IMPORTANT: You must add the following to your projects urls.py BEFORE any other registration/accounts/socialauth URL:
  ```
   from django_login_otp import views as otp_views

   urlpattens = [
        path('accounts/login/', otp_views.OtpLoginView.as_view(), name="login"),
        ...
   ]
  ```
        
 
You should override the enter_otp.html with your sites theme, CSS classes, etc.  The default is Bootstrap 5.2.

## Settings parameters

You can change the following parameters:

OTP_DONTASKAGAIN - How many Days in between OTP requests after they have confirmed one.  Default 7 days.
OTP_EXPIRY - How many minutes the OTP sent via Email is valid for. Default 15 minutes.
