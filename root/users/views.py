from . import models
from . import serializers
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from djoser.views import UserViewSet
from rest_framework import generics, viewsets
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response


 
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
    serializer_class = serializers.TreasureSerializer

    def get_queryset(self):
        return models.Treasure.objects.filter(user=self.request.user)
    
class TreasureView(generics.RetrieveUpdateAPIView, generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.TreasureSerializer

    def get_queryset(self):
        return models.Treasure.objects.filter(user=self.request.user)


class UserProfileView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.UserProfileSerializer

    def get_queryset(self):
        return models.UserProfile.objects.filter(user=self.request.user)
    
    
class EditUserProfileView(generics.RetrieveUpdateAPIView, generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.UserProfileSerializer

    def get_object(self):
        return models.UserProfile.objects.get(user=self.request.user)
    

class UserSettingsView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.UserSettingsSerializer

    def get_queryset(self):
        return models.UserSettings.objects.filter(user=self.request.user)
    

class ChangeUserSettingsView(generics.RetrieveUpdateAPIView, generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.UserSettingsSerializer

    def get_object(self):
        return models.UserSettings.objects.get(user=self.request.user)


class UserVisitsView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.UserVisitSerializer

    def get_queryset(self):
        return models.UserVisit.objects.filter(user=self.request.user)
    

class UserVisitView(generics.RetrieveUpdateAPIView, generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.UserVisitSerializer

    def get_queryset(self):
        return models.UserVisit.objects.filter(user=self.request.user)


class InboxView(generics.ListAPIView):
    queryset = models.Inbox.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Retrieve all items associated with the user
        return models.Item.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = serializers.ItemSerializer(queryset, many=True)  # Replace with your actual serializer
        return Response(serializer.data, status=status.HTTP_200_OK)

    
class ItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Item.objects.all()
    serializer_class = serializers.ItemSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        instance = self.get_object()

        # Mark the inbox item as read
        if not instance.is_read:
            instance.is_read = True
            instance.save()

        return super().get(request, *args, **kwargs)
    
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'success': 'Inbox item deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)


class MessageView(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Message.objects.all()
    serializer_class = serializers.MessageSerializer
    permission_classes = [AllowAny]

    def perform_destroy(self, instance):
        # Add any additional logic here if needed
        instance.delete()
        return Response({'success': 'Message deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)


class CreateMessageView(generics.CreateAPIView):
    queryset = models.Message.objects.all()
    serializer_class = serializers.MessageSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)



@api_view(['POST'])
def send_message(request):
    # Extract the message_id from the POST data
    message_id = request.data.get('message_id')
    
    # Retrieve the message based on the message_id
    message = get_object_or_404(models.Message, id=message_id)


    if request.user == message.recipient:
        return Response({'error': 'You cannot send a message to yourself.'}, status=status.HTTP_400_BAD_REQUEST)

    if message.sender != request.user:
        return Response({'error': 'You do not have permission to send this message.'}, status=status.HTTP_403_FORBIDDEN)

    # Optionally, mark the message as sent or handle other logic
    message.sent = True
    message.save()

    # Create the inbox item for the recipient
    inbox_item = models.Item.objects.create(content_object=message, user=message.recipient)
    inbox_item.save()
    
    return Response({'success': 'Message sent successfully.'}, status=status.HTTP_200_OK)


class SendFriendRequestView(generics.CreateAPIView):
    queryset = models.FriendRequest.objects.all()
    serializer_class = serializers.FriendRequestSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        sender = self.request.user
        recipient_id = self.request.data.get('recipient')
        message = self.request.data.get('message')
        recipient_id = recipient_id.id if hasattr(recipient_id, 'id') else recipient_id

        try:
            recipient = models.BadRainbowzUser.objects.get(pk=recipient_id)
        except models.BadRainbowzUser.DoesNotExist:
            raise PermissionDenied("Recipient user does not exist.")

        existing_request = models.FriendRequest.objects.filter(sender=sender, recipient=recipient)
        if existing_request.exists():
            return Response({'error': 'Friend request already sent.'}, status=status.HTTP_400_BAD_REQUEST)
        
        existing_friend = models.UserFriendship.objects.filter(user=sender, friend=recipient)
        if existing_friend.exists():
            return Response ({'error': 'You are already friends with this person.'}, status=status.HTTP_400_BAD_REQUEST)

        friend_request = serializer.save(sender=sender, recipient=recipient)

        friend_request_message = models.Message.objects.create(sender=sender, recipient=recipient, content=message)
        friend_request_message.content_object = friend_request
        friend_request_message.save()

        inbox_item = models.Item.objects.create(content_object=friend_request_message, user=recipient)
        inbox_item.save()

        return Response({'success': 'Friend request sent successfully.'}, status=status.HTTP_201_CREATED)


class FriendRequestDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.FriendRequest.objects.all()
    serializer_class = serializers.FriendRequestSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        friend_request_id = self.kwargs['item_view_id']
        return get_object_or_404(models.FriendRequest, id=friend_request_id)

    def perform_update(self, serializer):
        instance = self.get_object()
        accepted = self.request.data.get('is_accepted')

        print(f"Accepted: {accepted}")

        if accepted:
            user = self.request.user
            friend = instance.sender

            print(f"User: {user}, Friend: {friend}")

            friend_friendship_profile = models.UserFriendship.objects.create(user=user, friend=friend)
            print(f"Friend Friendship Profile: {friend_friendship_profile}")
            friend_friendship_profile.save()

            user_friendship_profile = models.UserFriendship.objects.create(user=friend, friend=user)
            print(f"User Friendship Profile: {user_friendship_profile}")
            user_friendship_profile.save()

            instance.delete()
            print("Request deleted")

            return Response({'success': 'Friend request accepted successfully!'}, status=status.HTTP_200_OK)
        else:
            
            serializer.save()
            return Response({'success': 'Friend request updated successfully!'}, status=status.HTTP_200_OK)


class UserFriendshipsView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.UserFriendshipSerializer

    def get_queryset(self):
        return models.UserFriendship.objects.filter(user=self.request.user)
    
class UserFriendshipView(generics.RetrieveUpdateAPIView, generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.UserFriendshipSerializer

    def get_queryset(self):
        return models.UserFriendship.objects.filter(user=self.request.user)


class SendGiftRequestView(generics.CreateAPIView):
    queryset = models.GiftRequest.objects.all()
    serializer_class = serializers.GiftRequestSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        sender = self.request.user
        recipient_id = self.request.data.get('recipient')
        message = self.request.data.get('message')
        treasure_id = self.request.data.get('treasure')
        
        recipient_id = recipient_id.id if hasattr(recipient_id, 'id') else recipient_id

        try:
            recipient = models.BadRainbowzUser.objects.get(pk=recipient_id)
        except models.BadRainbowzUser.DoesNotExist:
            raise PermissionDenied("Recipient user does not exist.")
        
        try:
            treasure = models.Treasure.objects.get(pk=treasure_id, user=sender)
            

            existing_request = models.GiftRequest.objects.filter(sender=sender, recipient=recipient, treasure=treasure)
            if existing_request.exists():
                return Response({'error': 'Duplicate request.'}, status=status.HTTP_400_BAD_REQUEST)
            
            existing_gift = models.GiftRequest.objects.filter(treasure=treasure)
            if existing_gift.exists():
                return Response ({'error': 'You have already sent a gift request for this item to someone else.'}, status=status.HTTP_400_BAD_REQUEST)


            gift_request = serializer.save(sender=sender, recipient=recipient, treasure=treasure)

            gift_request_message = models.Message.objects.create(sender=sender, recipient=recipient, content=message)
            gift_request_message.content_object = gift_request
            gift_request_message.save()

            inbox_item = models.Item.objects.create(content_object=gift_request_message, user=recipient)
            inbox_item.save()

            treasure.pending = True
            treasure.save()

        except models.Treasure.DoesNotExist:
            raise ValidationError("Treasure with the provided ID does not exist.")

        return Response({'success': 'Friend request sent successfully.'}, status=status.HTTP_201_CREATED)



class GiftRequestDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.GiftRequest.objects.all()
    serializer_class = serializers.GiftRequestSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        gift_request_id = self.kwargs['item_view_id']
        return get_object_or_404(models.GiftRequest, id=gift_request_id)

    def perform_update(self, serializer):
        instance = self.get_object()
        accepted = self.request.data.get('is_accepted')
        message = self.request.data.get('message')

        print(f"Accepted: {accepted}")

        if accepted:
            user = self.request.user
            friend = instance.sender

            treasure = instance.treasure
            treasure.accept(recipient=user, message=message)

            treasure.pending = False
            treasure.save()

            instance.delete()

            return Response({'success': 'Gift request accepted successfully!'}, status=status.HTTP_200_OK)
        else:
            
            serializer.save()
            return Response({'success': 'Gift request updated successfully!'}, status=status.HTTP_200_OK)
