from rest_framework import serializers
from accounts.models import Profile


class ProfileSerializers(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.id")

    class Meta:
        model = Profile
        fields = (
            "first_name",
            "last_name",
            "user",
            "bio",
            "birthdate",
            "email",
            "location",
            "gender",
            "picture",
            "slug",
            "update",
            "created"
        )
