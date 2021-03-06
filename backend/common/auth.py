from logging import getLogger

import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication

logger = getLogger(__name__)
USER_MODEL = get_user_model()


class JWTAuth(BaseAuthentication):
    """JSON Web Token Authentication class"""

    def authenticate(self, request):
        token = request.COOKIES.get('jwt')

        if not token:  # then user is not authenticated
            return None

        try:  # decode the jwt
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Token has expired!')

        # scope validation
        is_ambassador_url = 'api/ambassador' in request.path
        scope = payload.get('scope')
        if (is_ambassador_url and scope != 'ambassador') or \
                (not is_ambassador_url and scope != 'admin'):
            raise exceptions.AuthenticationFailed('Invalid scope!')

        try:  # get the user object
            user = USER_MODEL.objects.get(pk=payload.get('uid'))
        except USER_MODEL.DoesNotExist:
            raise exceptions.AuthenticationFailed('User not found!')

        # set login time
        user.last_login = timezone.now()
        user.save()

        return user, None

    @staticmethod
    def get_jwt(uid: int, scope: str):
        """Generates JWT with given user ID"""
        payload = {
            "uid": uid,  # user id
            "scope": scope,  # admin or ambassador
            "exp": timezone.now() + timezone.timedelta(minutes=15),  # expiry
            "iat": timezone.now()  # issued at
        }

        return jwt.encode(payload, settings.SECRET_KEY)  # algorithm = "HS256"
