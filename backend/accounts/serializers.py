from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User


class UserSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source="get_role_display", read_only=True)

    class Meta:
        model = User
        fields = [
            "id", "username", "email", "first_name", "last_name",
            "role", "role_display", "phone_number", "department",
            "is_active_staff",
        ]
        read_only_fields = ["id"]


class HIMSTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Extends the default JWT login serializer so the access token carries
    the user's role as a claim (useful for quick client-side checks) and
    the login response body includes the full user profile — the React
    frontend needs `role` immediately after login to decide which
    dashboard/menu to render (Section 3.3.2, frontend conditional
    rendering layer).
    """
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["role"] = user.role
        token["full_name"] = user.get_full_name()
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = UserSerializer(self.user).data
        return data
