from django.contrib.auth.views import LoginView
from django.contrib.auth import login as auth_login
from django.http import HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, get_object_or_404, redirect
from django import forms
from django.utils import timezone
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site

import secrets
import string
from datetime import timedelta

from .models import OTPUser

class OtpLoginView(LoginView):
    def form_valid(self, form):

        # If the user does not have an email then just go ahead and log them in.
        if not form.get_user().email or form.get_user().email == '':
            auth_login(self.request, form.get_user())
            messages.success(self.request, 'Successfully logged in')
            return HttpResponseRedirect(self.get_success_url())        


        email_stub = form.get_user().email.split('@')[1]

        # this is in MINUTES
        otp_expiry = 15
        try:
            if settings.OTP_EXPIRY:
                otp_expiry = settings.OTP_EXPIRY
        except AttributeError:
            pass          

        if 'otp' not in self.request.POST:
            print('OTP not in POST, check if we need to send one')

            # Check the last time an OTP was sent to the email address
            try:
                otp_user = OTPUser.objects.get(user=form.get_user())
            except ObjectDoesNotExist:
                otp_user = OTPUser(user=form.get_user())
                otp_user.save()

            # This is in DAYS
            ask_again = 7
            try:
                if settings.OTP_DONTASKAGAIN:
                    ask_again = settings.OTP_DONTASKAGAIN
            except AttributeError:
                pass

            expired = timezone.now() - timedelta(days=ask_again)

            if otp_user.last_valid_otp is not None and otp_user.last_valid_otp > expired:
                auth_login(self.request, form.get_user())
                messages.success(self.request, 'Successfully logged in')
                return HttpResponseRedirect(self.get_success_url())                

            if form.get_user().email:

                site = get_current_site(self.request)
                code_prefix = ''
                if ' ' in site.name:
                    site_words = site.name.split(' ')
                    for w in site_words:
                        code_prefix += w[0]
                else:
                    code_prefix = site.name[0:3]

                # Generate a new One Time Password to be sent by Email
                otp = code_prefix.upper() + '-'
                otp += ''.join(secrets.choice(string.ascii_uppercase) for i in range(1))
                otp += ''.join(secrets.choice(string.digits) for i in range (3))
                otp += '-'
                otp += ''.join(secrets.choice(string.ascii_uppercase) for i in range(4))
                otp += '-'
                otp += ''.join(secrets.choice(string.digits) for i in range (4))

                otp_user.current_otp = otp
                otp_user.current_otp_sent = timezone.now()
                otp_user.save()

                email_body = render_to_string('registration/email_code.html', {'user': otp_user, 'expiry': otp_expiry, 'site': site })

                send_mail(
                    'Your single use code',
                    email_body,
                    None,
                    [otp_user.user.email]
                )

                messages.success(self.request, 'Code sent to email ending in @' + email_stub)
        else:
            # If we DO have an OTP then compare it against the user
            otp_user = get_object_or_404(OTPUser, user=form.get_user())
            otp = self.request.POST.get('otp', None)

            # Is the OTP valid?
            if otp_user.current_otp_sent and otp_user.current_otp_sent > (timezone.now() - timedelta(minutes=otp_expiry)):
                # Compare the given OTP to the code
                # First check length of OTP
                if len(otp) == len(otp_user.current_otp) and '-' in otp and otp.count('-') == 3 and otp == otp_user.current_otp:
                    otp_user.last_valid_otp = timezone.now()
                    otp_user.save()

                    auth_login(self.request, form.get_user())
                    messages.success(self.request, 'Successfully logged in')
                    return HttpResponseRedirect(self.get_success_url())
                    
                messages.error(self.request, 'Invalid OTP Code')
            else:
                messages.error(self.request, 'OTP Code has expired')
                return redirect('login')


        form.fields['otp'] = forms.CharField(widget=forms.TextInput(), required=True, label='Code')
        return render(self.request, 'registration/enter_otp.html', {'form': form, 'email_stub': email_stub})