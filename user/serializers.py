from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from django.utils.translation import gettext as _


class UserSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=70, required=True)
    last_name = serializers.CharField(max_length=70, required=True)

    class Meta:
        model = get_user_model()
        fields = ("id", "first_name", "last_name", "email", "password")
        extra_kwargs = {
            "password": {
                "write_only": True,
                "style": {"input_type": "password"},
                "label": _("Password"),
            }
        }

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validate_date):
        return get_user_model().objects.create_user(**validate_date)

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user
