from . import models
from . import serializers
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from djoser.views import UserViewSet
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, throttling, viewsets
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes, throttle_classes
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


@swagger_auto_schema(operation_id='activateUser', auto_schema=None)
class ActivateUser(UserViewSet):

    
    @swagger_auto_schema(operation_id='getSerializerForActivate')
    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs.setdefault('context', self.get_serializer_context())
 
        #This line is the only diversion from original implementation.
        kwargs['data'] = {"uid": self.kwargs['uid'], "token": self.kwargs['token']}
 
        return serializer_class(*args, **kwargs)
    
    def activation(self, request, uid, token, *args, **kwargs):
        super().activation(request, *args, **kwargs)
        return Response(status=status.HTTP_204_NO_CONTENT)


@swagger_auto_schema(operation_id='resetUsername')
class UsernameReset(UserViewSet):
    pass


@swagger_auto_schema(operation_id='resetPassword')
class PasswordReset(UserViewSet):
    pass
   

@swagger_auto_schema(operation_id='listTreasures')
class TreasuresView(generics.ListCreateAPIView):
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [AllowAny]
    serializer_class = serializers.TreasureSerializer
    throttle_classes = [throttling.AnonRateThrottle, throttling.UserRateThrottle]

    def get_queryset(self):
        return models.Treasure.objects.filter(user=self.request.user)
    

@swagger_auto_schema(operation_id='treasureOperations')
class TreasureView(generics.RetrieveUpdateAPIView, generics.DestroyAPIView):
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [AllowAny]
    serializer_class = serializers.TreasureSerializer
    throttle_classes = [throttling.AnonRateThrottle, throttling.UserRateThrottle]

    def get_queryset(self):
        return models.Treasure.objects.filter(user=self.request.user)


@swagger_auto_schema(operation_id='listUserProfile')
class UserProfileView(generics.ListCreateAPIView):
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [AllowAny]
    serializer_class = serializers.UserProfileSerializer
    throttle_classes = [throttling.AnonRateThrottle, throttling.UserRateThrottle]

    def get_queryset(self):
        return models.UserProfile.objects.filter(user=self.request.user)
    
    
@swagger_auto_schema(operation_id='editUserProfile')
class EditUserProfileView(generics.RetrieveUpdateAPIView, generics.DestroyAPIView):
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [AllowAny]
    serializer_class = serializers.UserProfileSerializer
    throttle_classes = [throttling.AnonRateThrottle, throttling.UserRateThrottle]

    def get_object(self):
        return models.UserProfile.objects.get(user=self.request.user)
    

@swagger_auto_schema(operation_id='listUserSettings')
class UserSettingsView(generics.ListCreateAPIView):
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [AllowAny]
    serializer_class = serializers.UserSettingsSerializer
    throttle_classes = [throttling.AnonRateThrottle, throttling.UserRateThrottle]

    def get_queryset(self):
        return models.UserSettings.objects.filter(user=self.request.user)


@swagger_auto_schema(operation_id='editUserSettings')
class ChangeUserSettingsView(generics.RetrieveUpdateAPIView, generics.DestroyAPIView):
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [AllowAny]
    serializer_class = serializers.UserSettingsSerializer
    throttle_classes = [throttling.AnonRateThrottle, throttling.UserRateThrottle]

    def get_object(self):
        return models.UserSettings.objects.get(user=self.request.user)


@swagger_auto_schema(operation_id='listUserVisits')
class UserVisitsView(generics.ListCreateAPIView):
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [AllowAny]
    serializer_class = serializers.UserVisitSerializer
    throttle_classes = [throttling.AnonRateThrottle, throttling.UserRateThrottle]

    def get_queryset(self):
        return models.UserVisit.objects.filter(user=self.request.user)
    

@swagger_auto_schema(operation_id='userVisitOperations')
class UserVisitView(generics.RetrieveUpdateAPIView, generics.DestroyAPIView):
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [AllowAny]
    serializer_class = serializers.UserVisitSerializer
    throttle_classes = [throttling.AnonRateThrottle, throttling.UserRateThrottle]

    def get_queryset(self):
        return models.UserVisit.objects.filter(user=self.request.user)


@swagger_auto_schema(operation_id='listInbox')
class InboxView(generics.ListAPIView):
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [AllowAny]
    serializer_class = serializers.InboxSerializer
    throttle_classes = [throttling.AnonRateThrottle, throttling.UserRateThrottle]

    queryset = models.Inbox.objects.all()

    def get_queryset(self):
        return models.Item.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = serializers.ItemSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@swagger_auto_schema(operation_id='itemOperations')
class ItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [AllowAny]
    serializer_class = serializers.ItemSerializer
    throttle_classes = [throttling.AnonRateThrottle, throttling.UserRateThrottle]

    queryset = models.Item.objects.all()

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


@swagger_auto_schema(operation_id='messageOperations')
class MessageView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [AllowAny]
    serializer_class = serializers.MessageSerializer
    throttle_classes = [throttling.AnonRateThrottle, throttling.UserRateThrottle]

    queryset = models.Message.objects.all()

    def perform_destroy(self, instance):
        instance.delete()
        return Response({'success': 'Message deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)


@swagger_auto_schema(operation_id='createMessage')
class CreateMessageView(generics.CreateAPIView):
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    serializer_class = serializers.MessageSerializer
    permission_classes = [AllowAny]
    throttle_classes = [throttling.AnonRateThrottle, throttling.UserRateThrottle]

    queryset = models.Message.objects.all()

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)


@api_view(['POST'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@throttle_classes([AnonRateThrottle, UserRateThrottle])
@swagger_auto_schema(operation_id='sendMessage')
def send_message(request):
    message_id = request.data.get('message_id')
    
    message = get_object_or_404(models.Message, id=message_id)


    if request.user == message.recipient:
        return Response({'error': 'You cannot send a message to yourself.'}, status=status.HTTP_400_BAD_REQUEST)

    if message.sender != request.user:
        return Response({'error': 'You do not have permission to send this message.'}, status=status.HTTP_403_FORBIDDEN)

    message.sent = True
    message.save()

    inbox_item = models.Item.objects.create(content_object=message, user=message.recipient)
    inbox_item.save()
    
    return Response({'success': 'Message sent successfully.'}, status=status.HTTP_200_OK)


@swagger_auto_schema(operation_id='createFriendRequest')
class SendFriendRequestView(generics.CreateAPIView):
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [AllowAny]
    serializer_class = serializers.FriendRequestSerializer
    throttle_classes = [throttling.AnonRateThrottle, throttling.UserRateThrottle]

    queryset = models.FriendRequest.objects.all()

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


@swagger_auto_schema(operation_id='friendRequestOperations')
class FriendRequestDetailView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [AllowAny]
    serializer_class = serializers.FriendRequestSerializer
    throttle_classes = [throttling.AnonRateThrottle, throttling.UserRateThrottle]

    queryset = models.FriendRequest.objects.all()

    def get_object(self):
        friend_request_id = self.kwargs['item_view_id']
        return get_object_or_404(models.FriendRequest, id=friend_request_id)

    def perform_update(self, serializer):
        instance = self.get_object()
        rejected = self.request.data.get('is_rejected')
        accepted = self.request.data.get('is_accepted')

        print(f"Accepted: {accepted}")

        if rejected:
            instance.delete()

            return Response({'success': 'Friend request rejected successfully!'}, status=status.HTTP_200_OK)

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


@swagger_auto_schema(operation_id='listUserFriendships')
class UserFriendshipsView(generics.ListCreateAPIView):
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [AllowAny]
    serializer_class = serializers.UserFriendshipSerializer
    throttle_classes = [throttling.AnonRateThrottle, throttling.UserRateThrottle]

    def get_queryset(self):
        return models.UserFriendship.objects.filter(user=self.request.user)
    

@swagger_auto_schema(operation_id='userFriendshipOperations')
class UserFriendshipView(generics.RetrieveUpdateAPIView, generics.DestroyAPIView):
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [AllowAny]
    serializer_class = serializers.UserFriendshipSerializer
    throttle_classes = [throttling.AnonRateThrottle, throttling.UserRateThrottle]

    def get_queryset(self):
        return models.UserFriendship.objects.filter(user=self.request.user)


@swagger_auto_schema(operation_id='createGiftRequest')
class SendGiftRequestView(generics.CreateAPIView):
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [AllowAny]
    serializer_class = serializers.GiftRequestSerializer
    throttle_classes = [throttling.AnonRateThrottle, throttling.UserRateThrottle]

    queryset = models.GiftRequest.objects.all()
    

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


@swagger_auto_schema(operation_id='giftRequest')
class GiftRequestDetailView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [AllowAny]
    serializer_class = serializers.GiftRequestSerializer
    throttle_classes = [throttling.AnonRateThrottle, throttling.UserRateThrottle]

    queryset = models.GiftRequest.objects.all()

    def get_object(self):
        gift_request_id = self.kwargs['item_view_id']
        return get_object_or_404(models.GiftRequest, id=gift_request_id)

    def perform_update(self, serializer):
        instance = self.get_object()
        rejected = self.request.data.get('is_rejected')
        accepted = self.request.data.get('is_accepted')
        message = self.request.data.get('message')

        print(f"Accepted: {accepted}")

        if rejected:
            instance.delete()

            return Response({'success': 'Gift request rejected successfully!'}, status=status.HTTP_200_OK)

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
