from django.db import models
from django.conf import settings

class OTPUser(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    last_valid_otp = models.DateTimeField(blank=True, null=True)
    current_otp_sent = models.DateTimeField(blank=True, null=True)
    current_otp = models.CharField(max_length=25, blank=True)

    class Meta:
        verbose_name = "User"

