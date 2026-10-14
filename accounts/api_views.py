from rest_framework import views, permissions, status
from rest_framework.response import Response
from .serializers import UserSerializer


class CurrentUserAPIView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
