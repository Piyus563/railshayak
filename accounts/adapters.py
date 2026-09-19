from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.adapter import DefaultAccountAdapter
from django.contrib import messages


class RailSaathiAccountAdapter(DefaultAccountAdapter):
    def get_login_redirect_url(self, request):
        return '/accounts/dashboard/'


class RailSaathiSocialAccountAdapter(DefaultSocialAccountAdapter):

    def pre_social_login(self, request, sociallogin):
        """
        If a user with the same email already exists, connect the social
        account to that existing user instead of creating a duplicate.
        """
        from accounts.models import User
        if sociallogin.is_existing:
            return
        email = sociallogin.account.extra_data.get('email', '').lower()
        if not email:
            return
        try:
            existing_user = User.objects.get(email__iexact=email)
            sociallogin.connect(request, existing_user)
        except User.DoesNotExist:
            pass

    def save_user(self, request, sociallogin, form=None):
        """
        Save the new user and auto-create PassengerProfile + set role.
        """
        from accounts.models import User, PassengerProfile
        user = super().save_user(request, sociallogin, form)

        # Set default role to PASSENGER for Google sign-ups
        if not user.role or user.role == '':
            user.role = 'PASSENGER'

        # Set username from email if not set
        if not user.username or user.username == user.email:
            base = user.email.split('@')[0].replace('.', '_').lower()
            username = base
            counter = 1
            while User.objects.filter(username=username).exclude(pk=user.pk).exists():
                username = f"{base}{counter}"
                counter += 1
            user.username = username

        user.save(update_fields=['role', 'username'])

        # Auto-create PassengerProfile if not exists
        PassengerProfile.objects.get_or_create(user=user)

        return user

    def get_connect_redirect_url(self, request, socialaccount):
        return '/accounts/dashboard/'
