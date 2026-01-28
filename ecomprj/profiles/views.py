from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import ProfileSerializer, UserSerializer

class ProfileView(APIView):
  permission_classes = [IsAuthenticated]

  def get(self, request):
    return Response({
      "user": UserSerializer(request.user).data,
      "profile": ProfileSerializer(request.user.profile).data
    })

  def put(self, request):
    user_serializer = UserSerializer(
      request.user,
      data=request.data.get('user', {}),
      partial=True
    )

    profile_serializer = ProfileSerializer(
      request.user.profile,
      data=request.data.get('profile', {}),
      partial=True
    )

    user_serializer.is_valid(raise_exception=True)
    profile_serializer.is_valid(raise_exception=True)

    user_serializer.save()
    profile_serializer.save()

    return Response({
      "user": user_serializer.data,
      "profile": profile_serializer.data
    })
