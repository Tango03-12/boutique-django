from django.contrib.auth import get_user_model

User = get_user_model()

class TelephoneBackend:
    def authenticate(self, request, username=None, password=None):
        try:
            user = User.objects.get(telephone=username)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None
