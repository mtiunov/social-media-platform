import django_filters
from accounts.models import Profile


class ProfileFilter(django_filters.FilterSet):
    class Meta:
        model = Profile
        fields = {
            "username": ["iexact", "icontains"],
            "bio": ["iexact", "icontains"],
            "gender": ["iexact"],
            "location": ["iexact"],
            "birthdate": ["exact", "lt", "gt"],
        }
