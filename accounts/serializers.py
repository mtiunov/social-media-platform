from datetime import date

from rest_framework import serializers
from accounts.models import Profile


class ProfileSerializers(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.id")
    full_name = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = (
            "id",
            "first_name",
            "last_name",
            "full_name",
            "user",
            "username",
            "bio",
            "birthdate",
            "age",
            "email",
            "location",
            "gender",
            "picture",
            "slug",
            "update",
            "created"
        )

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    def get_age(self, obj):
        if obj.birthdate:
            today = date.today()
            return today.year - obj.birthdate.year - \
                ((today.month, today.day) < (obj.birthdate.month, obj.birthdate.day))
        return None
