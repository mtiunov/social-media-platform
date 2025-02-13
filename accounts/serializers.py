from rest_framework import serializers
from accounts.models import Profile


class ProfileSerializers(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = (
            "first_name",
            "last_name",
            "user", "bio",
            "birthdate",
            "email",
            "location",
            "gender",
            "picture",
            "slug",
            "friends",
            "update",
            "created"
        )
