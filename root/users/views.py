from django.shortcuts import render
from djoser.views import UserViewSet
from .models import BadRainbowzUser, ItemInbox, Treasure, UserProfile, UserSettings, UserVisit
from rest_framework import generics, viewsets
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import TreasureSerializer, UserProfileSerializer, UserSettingsSerializer, UserVisitSerializer

 
class ActivateUser(UserViewSet):
    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs.setdefault('context', self.get_serializer_context())
 
        #This line is the only diversion from original implementation.
        kwargs['data'] = {"uid": self.kwargs['uid'], "token": self.kwargs['token']}
 
        return serializer_class(*args, **kwargs)
 
    def activation(self, request, uid, token, *args, **kwargs):
        super().activation(request, *args, **kwargs)
        return Response(status=status.HTTP_204_NO_CONTENT)


class UsernameReset(UserViewSet):
    pass

class PasswordReset(UserViewSet):
 
    pass
    

class TreasuresView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TreasureSerializer

    def get_queryset(self):
        return Treasure.objects.filter(user=self.request.user)
    
class TreasureView(generics.RetrieveUpdateAPIView, generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TreasureSerializer

    def get_queryset(self):
        return Treasure.objects.filter(user=self.request.user)


class UserProfileView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer

    def get_queryset(self):
        return UserProfile.objects.filter(user=self.request.user)
    
    
class EditUserProfileView(generics.RetrieveUpdateAPIView, generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer

    def get_object(self):
        return UserProfile.objects.get(user=self.request.user)
    

class UserSettingsView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSettingsSerializer

    def get_queryset(self):
        return UserSettings.objects.filter(user=self.request.user)
    

class ChangeUserSettingsView(generics.RetrieveUpdateAPIView, generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSettingsSerializer

    def get_object(self):
        return UserSettings.objects.get(user=self.request.user)


class UserVisitsView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserVisitSerializer

    def get_queryset(self):
        return UserVisit.objects.filter(user=self.request.user)
    
class UserVisitView(generics.RetrieveUpdateAPIView, generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserVisitSerializer

    def get_queryset(self):
        return UserVisit.objects.filter(user=self.request.user)



