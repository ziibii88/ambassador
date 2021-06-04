from logging import getLogger

from django.contrib.auth import get_user_model
from rest_framework import serializers

logger = getLogger(__name__)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = '__all__'
        read_only_fields = (
            'last_login', 'date_joined', 'groups', 'user_permissions',
            'is_active', 'is_staff', 'is_superuser')
        extra_kwargs = {
            'password': {
                'write_only': True,  # does not expose field in GET
                'min_length': 8,  # minimum length of password
                'style': {'input_type': 'password'},  # for browsable API
        }}

    def create(self, validated_data):
        """Overriding to handle with custom user manager"""
        logger.debug(
            f"Creating user: email={validated_data.get('email', None)}")
        return self.Meta.model.objects.create_user(**validated_data)