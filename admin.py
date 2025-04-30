from django.contrib import admin

from django.apps import apps

core_models = apps.get_app_config('django_login_otp').get_models()

# Register your models here.
from .models import *

# Register all

for model in core_models:
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass