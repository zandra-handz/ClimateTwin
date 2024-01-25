from django.shortcuts import render
from rest_framework import generics, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import ClimateTwinLocation
from .serializers import ClimateTwinLocationSerializer

# Create your views here.
def index(request):
    return render(request, 'index.html', {})

class ClimateTwinLocationsView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ClimateTwinLocationSerializer

    def get_queryset(self):
        # Filter locations based on the logged-in user
        return ClimateTwinLocation.objects.filter(user=self.request.user)
class ClimateTwinLocationView(generics.RetrieveUpdateAPIView, generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ClimateTwinLocationSerializer

    def get_queryset(self):
        # Filter locations based on the logged-in user
        return ClimateTwinLocation.objects.filter(user=self.request.user)

class ClimateTwinLocationViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ClimateTwinLocationSerializer

    def get_queryset(self):
        # Filter locations based on the logged-in user
        return ClimateTwinLocation.objects.filter(user=self.request.user)