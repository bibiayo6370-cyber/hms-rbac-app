from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from core.models import AuditLog
from .serializers import HIMSTokenObtainPairSerializer, UserSerializer


def _client_ip(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    return forwarded.split(",")[0] if forwarded else request.META.get("REMOTE_ADDR")


class LoginView(TokenObtainPairView):
    """
    POST /api/auth/login/  { "username": ..., "password": ... }
    Returns access + refresh tokens plus the authenticated user's profile.
    Every login attempt (success or failure) is written to the audit log,
    supporting the accountability principle in Section 3.7.2.
    """
    serializer_class = HIMSTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        username = request.data.get("username", "")
        if response.status_code == 200:
            from .models import User
            user = User.objects.filter(username=username).first()
            AuditLog.objects.create(
                user=user, action=AuditLog.Action.LOGIN,
                entity_type="User", entity_id=str(user.id) if user else "",
                description=f"Successful login for '{username}'",
                ip_address=_client_ip(request),
            )
        else:
            AuditLog.objects.create(
                user=None, action=AuditLog.Action.LOGIN_FAILED,
                entity_type="User", entity_id="",
                description=f"Failed login attempt for '{username}'",
                ip_address=_client_ip(request),
            )
        return response


class MeView(APIView):
    """GET /api/auth/me/ — returns the currently authenticated user's profile."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)
