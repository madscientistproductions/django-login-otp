from django.contrib import admin
from django_login_otp.models import OTPUser

class OTPUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'last_valid_otp', 'current_otp_sent')

admin.site.register(OTPUser, OTPUserAdmin)
