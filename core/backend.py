import re
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()


class PhoneOrEmailBackend(ModelBackend):
    """
    Authenticate a user using either their email address or their phone number.

    Looks for an `identifier` argument first, then `username`. If the identifier
    looks like an email, it will search the User.email field. Otherwise it will
    try to find a related Profile with a matching `phone_number`.
    """

    email_regex = re.compile(r'^[\w\.-]+@[\w\.-]+\.\w+$')

    def authenticate(self, request, username=None, password=None, identifier=None, **kwargs):
        ident = identifier or username or kwargs.get('email')
        if not ident or not password:
            return None

        user = None
        try:
            if self.email_regex.match(ident):
                user = User.objects.get(email__iexact=ident)
            else:
                # try to find user via related Profile.phone_number (safe)
                for u in User.objects.all():
                    profile = getattr(u, 'profiles', None)
                    if profile and profile.phone_number == ident:
                        user = u
                        break
                # fallback: maybe phone_number stored on User directly
                if not user and hasattr(User, 'phone_number'):
                    user = User.objects.filter(phone_number=ident).first()

            if user and user.check_password(password):
                return user
        except User.DoesNotExist:
            return None

        # return None