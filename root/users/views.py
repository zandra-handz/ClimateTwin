from . import models
from . import serializers
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from djoser.views import UserViewSet
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, throttling, viewsets
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes, throttle_classes
from rest_framework.exceptions import PermissionDenied, MethodNotAllowed
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
   

class TreasuresView(generics.ListCreateAPIView):
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [AllowAny]
    serializer_class = serializers.TreasureSerializer
    throttle_classes = [throttling.AnonRateThrottle, throttling.UserRateThrottle]

    @swagger_auto_schema(operation_id='listUserTreasures', operation_description="Returns user treasures.")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @swagger_auto_schema(operation_id='createUserTreasure', auto_schema=None)
    def post(self, request, *args, **kwargs):
        raise MethodNotAllowed('POST')

    def get_queryset(self):
        return models.Treasure.objects.filter(user=self.request.user)
    

class TreasureView(generics.RetrieveAPIView, generics.DestroyAPIView):
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [AllowAny]
    serializer_class = serializers.TreasureSerializer
    throttle_classes = [throttling.AnonRateThrottle, throttling.UserRateThrottle]

    @swagger_auto_schema(operation_id='getUserTreasure', operation_description="Returns treasure.")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(operation_id='deleteUserTreasure', operation_description="Deletes treasure.")
    def delete(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    def get_queryset(self):
        return models.Treasure.objects.filter(user=self.request.user)



class UserProfileView(generics.ListCreateAPIView):
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [AllowAny]
    serializer_class = serializers.UserProfileSerializer
    throttle_classes = [throttling.AnonRateThrottle, throttling.UserRateThrottle]
    
    @swagger_auto_schema(operation_id='createUserProfile', operation_description="Creates user profile.")
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    @swagger_auto_schema(operation_id='getUserProfile', operation_description="Returns user profile.")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return models.UserProfile.objects.filter(user=self.request.user)
    
    
class EditUserProfileView(generics.RetrieveUpdateAPIView, generics.DestroyAPIView):
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [AllowAny]
    serializer_class = serializers.UserProfileSerializer
    throttle_classes = [throttling.AnonRateThrottle, throttling.UserRateThrottle]


    @swagger_auto_schema(operation_id='getUserProfileToEdit', operation_description="Returns user profile in edit view.")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(operation_id='updateUserProfile', operation_description="Updates user profile.")
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(operation_id='partialUpdateUserProfile', operation_description="Updates user profile via PATCH.", auto_schema=None)
    def patch(self, request, *args, **kwargs):
        raise MethodNotAllowed('PATCH')

    @swagger_auto_schema(operation_id='deleteUserProfile', operation_description="Deletes user profile.", auto_schema=None)
    def delete(self, request, *args, **kwargs):
        raise MethodNotAllowed('DELETE')

    def get_queryset(self):
        return models.UserProfile.objects.filter(user=self.request.user)



class UserSettingsView(generics.ListCreateAPIView):
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [AllowAny]
    serializer_class = serializers.UserSettingsSerializer
    throttle_classes = [throttling.AnonRateThrottle, throttling.UserRateThrottle]

    @swagger_auto_schema(operation_id='createUserSettings', operation_description="Creates user settings.")
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    @swagger_auto_schema(operation_id='getUserSettings', operation_description="Returns user settings.")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return models.UserSettings.objects.filter(user=self.request.user)


class ChangeUserSettingsView(generics.RetrieveUpdateAPIView):
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [AllowAny]
    serializer_class = serializers.UserSettingsSerializer
    throttle_classes = [throttling.AnonRateThrottle, throttling.UserRateThrottle]

    @swagger_auto_schema(operation_id='getUserSettingsToChnage', operation_description="Returns user settings in change view.")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(operation_id='updateUserSettings', operation_description="Updates user settings.")
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(operation_id='partialUpdateUserSettings', operation_description="Updates user settings via PATCH.", auto_schema=None)
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    def get_queryset(self):
        return models.UserSettings.objects.filter(user=self.request.user)
    

class UserVisitsView(generics.ListAPIView):
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [AllowAny]
    serializer_class = serializers.UserVisitSerializer
    throttle_classes = [throttling.AnonRateThrottle, throttling.UserRateThrottle]

    @swagger_auto_schema(operation_id='listUserVisits', operation_description="Returns user visits.")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    def get_queryset(self):
        return models.UserVisit.objects.filter(user=self.request.user)
    

class UserVisitView(generics.RetrieveAPIView, generics.DestroyAPIView):
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [AllowAny]
    serializer_class = serializers.UserVisitSerializer
    throttle_classes = [throttling.AnonRateThrottle, throttling.UserRateThrottle]

    @swagger_auto_schema(operation_id='getUserVisit', operation_description="Returns user visit.")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(operation_id='deleteUserVisit', operation_description="Deletes user visit.")
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

    def get_queryset(self):
        return models.UserVisit.objects.filter(user=self.request.user)


class InboxView(generics.ListAPIView):
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [AllowAny]
    serializer_class = serializers.InboxSerializer
    throttle_classes = [throttling.AnonRateThrottle, throttling.UserRateThrottle]

    queryset = models.Inbox.objects.all()

    @swagger_auto_schema(operation_id='getInboxItems', operation_description="Returns inbox items.")
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = serializers.InboxItemSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_queryset(self):
        return models.InboxItem.objects.filter(user=self.request.user)



class InboxItemDetailView(generics.RetrieveDestroyAPIView):
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [AllowAny]
    serializer_class = serializers.InboxItemSerializer
    throttle_classes = [throttling.AnonRateThrottle, throttling.UserRateThrottle]

    queryset = models.InboxItem.objects.all()

    @swagger_auto_schema(operation_id="getInboxItem", operation_description="Returns inbox item and marks as read.")
    def get(self, request, *args, **kwargs):
        instance = self.get_object()

        # Mark the inbox item as read
        if not instance.is_read:
            instance.is_read = True
            instance.save()

        try:
            message = models.Message.objects.get(pk=instance.message.id)
        except models.Message.DoesNotExist:
            return Response({"error": "Message does not exist"}, status=status.HTTP_404_NOT_FOUND)

        # Serialize the Message object using MessageSerializer
        message_serializer = serializers.MessageSerializer(message)

        # Serialize the InboxItem instance
        inbox_item_serializer = self.get_serializer(instance)

        # Modify the serialized InboxItem data to include the serialized message data
        serialized_data = inbox_item_serializer.data
        serialized_data['message'] = message_serializer.data

        # Return the response generated by super().get(request, *args, **kwargs)
        return Response(serialized_data)
    
    #test this
    @swagger_auto_schema(operation_id="deleteInboxItem", operation_description="Deletes inbox item.")
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.delete(instance)
        return Response({'success': 'Inbox item deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)


class MessageView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [AllowAny]
    serializer_class = serializers.MessageSerializer
    throttle_classes = [throttling.AnonRateThrottle, throttling.UserRateThrottle]

    queryset = models.Message.objects.all()

    @swagger_auto_schema(operation_id='getMessage', operation_description="Returns message.")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(operation_id='updateMessage', operation_description="Updates message.")
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(operation_id='partialUpdateMessage', operation_description="Updates message via PATCH.", auto_schema=None)
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @swagger_auto_schema(operation_id='deleteMessage', operation_description="Deletes message.")
    def delete(self, instance):
        instance.delete()
        return Response({'success': 'Message deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)



class CreateMessageView(generics.CreateAPIView):
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    serializer_class = serializers.MessageSerializer
    permission_classes = [AllowAny]
    throttle_classes = [throttling.AnonRateThrottle, throttling.UserRateThrottle]

    queryset = models.Message.objects.all()
    @swagger_auto_schema(operation_id='createMessage', operation_description="Creates message.")
    def post(self, serializer):
        serializer.save(sender=self.request.user)


@swagger_auto_schema(method='post', operation_id='sendMessage', request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'message_id': openapi.Schema(type=openapi.TYPE_INTEGER, description="ID of message draft to send.")
        },
        required=['message_id'],
    ), operation_dscription="Sends message.")
@api_view(['POST'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@throttle_classes([AnonRateThrottle, UserRateThrottle])
def send_message(request):
    message_id = request.data.get('message_id')
    
    message = get_object_or_404(models.Message, id=message_id)


    if request.user == message.recipient:
        return Response({'error': 'You cannot send a message to yourself.'}, status=status.HTTP_400_BAD_REQUEST)

    if message.sender != request.user:
        return Response({'error': 'You do not have permission to send this message.'}, status=status.HTTP_403_FORBIDDEN)

    message.sent = True
    message.save()

    inbox_item = models.InboxItem.objects.create(content_object=message, user=message.recipient)
    inbox_item.save()
    
    return Response({'success': 'Message sent successfully.'}, status=status.HTTP_200_OK)


# Test this (2/22)
class SendFriendRequestView(generics.CreateAPIView):
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [AllowAny]
    serializer_class = serializers.FriendRequestSerializer
    throttle_classes = [throttling.AnonRateThrottle, throttling.UserRateThrottle]

    queryset = models.FriendRequest.objects.all()

    
    @swagger_auto_schema(operation_id='createFriendRequest')
    def post(self, request, *args, **kwargs):
        sender = self.request.user
        message = self.request.data.get('message')

        try:
            recipient = models.BadRainbowzUser.objects.get(pk=request.data['recipient'])
        except models.BadRainbowzUser.DoesNotExist:
            raise PermissionDenied("Recipient user does not exist.")

        existing_request = models.FriendRequest.objects.filter(sender=request.user, recipient=recipient)
        if existing_request.exists():
            return Response({'error': 'Friend request already sent.'}, status=status.HTTP_400_BAD_REQUEST)
        
        #this should be friendship model
        existing_friendship = models.Friendship.objects.filter(initiator=request.user, reciprocator=recipient)
        if existing_friendship.exists():
            return Response ({'error': 'You are already friends with this person.'}, status=status.HTTP_400_BAD_REQUEST)


        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        friend_request = serializer.save(sender=request.user, recipient=recipient)

        friend_request_message = models.Message.objects.create(sender=request.user, recipient=recipient, content=message)
        friend_request_message.content_object = friend_request
        friend_request_message.save()


        inbox_item = models.InboxItem.objects.create(user=recipient, message=friend_request_message)
        inbox_item.save()

        return Response({'success': 'Friend request sent successfully.'}, status=status.HTTP_201_CREATED)



class FriendRequestDetailView(generics.RetrieveUpdateAPIView):
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [AllowAny]
    serializer_class = serializers.AcceptRejectFriendRequestSerializer
    throttle_classes = [throttling.AnonRateThrottle, throttling.UserRateThrottle]


    queryset = models.FriendRequest.objects.all()

    def get_object(self):
        friend_request_id = self.kwargs['item_view_id']
        return get_object_or_404(models.FriendRequest, id=friend_request_id)


    @swagger_auto_schema(operation_id="getFriendRequest", operation_description="Gets friend request.")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    

    @swagger_auto_schema(operation_id="replyFriendRequest", operation_description="Updates is_rejected or is_accepted on friend request, creates frienship instance if accepted, deletes friend request either way.")
    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        rejected = request.data.get('is_rejected')
        accepted = request.data.get('is_accepted')


        if accepted is not None:
            user = request.user
            friend = instance.sender
            friendship = models.Friendship.objects.create(initiator=friend, reciprocator=user)

            friend_friendship_profile = models.FriendProfile.objects.create(user=user, friend=friend, friendship=friendship)
            friend_friendship_profile.save()

            user_friendship_profile = models.FriendProfile.objects.create(user=friend, friend=user, friendship=friendship)
            user_friendship_profile.save()

            with transaction.atomic():
                instance.delete()

            return Response({'success': 'Friend request accepted successfully!'}, status=status.HTTP_200_OK)
        
        if rejected is not None: 

            with transaction.atomic():
                instance.delete()

            return Response({'success': 'Friend request rejected successfully!'}, status=status.HTTP_200_OK)

        return Response({'error': 'You must provide either "is_accepted" or "is_rejected" field.'}, status=status.HTTP_400_BAD_REQUEST)



    @swagger_auto_schema(operation_id="partialUpdateFriendRequest", operation_description="Updates friend request via PATCH", auto_schema=None)
    def patch(self, request, *args, **kwargs):
        raise MethodNotAllowed('PATCH')

        


class FriendProfilesView(generics.ListAPIView):
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [AllowAny]
    serializer_class = serializers.FriendProfileSerializer
    throttle_classes = [throttling.AnonRateThrottle, throttling.UserRateThrottle]

    @swagger_auto_schema(operation_id='listFriendProfiles', operation_description="Returns friend profiles.")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return models.FriendProfile.objects.filter(user=self.request.user)
    


class FriendProfileView(generics.RetrieveUpdateAPIView):
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [AllowAny]
    serializer_class = serializers.FriendProfileSerializer
    throttle_classes = [throttling.AnonRateThrottle, throttling.UserRateThrottle]

    @swagger_auto_schema(operation_id='getFriendProfile', operation_description="Returns friend profile.")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(operation_id='updateFriendProfile', operation_description="Updates friend profile.")
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(operation_id='partialUpdateFriendProfile', operation_description="Updates user friend profile via PATCH.", auto_schema=None)
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    def get_queryset(self):
        return models.FriendProfile.objects.filter(user=self.request.user)
    
    
class DeleteFriendshipView(generics.DestroyAPIView):
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [AllowAny]
    serializer_class = serializers.FriendshipSerializer
    throttle_classes = [throttling.AnonRateThrottle, throttling.UserRateThrottle]

    @swagger_auto_schema(operation_id='deleteFriendship', operation_description="Deletes friendship.")
    def delete(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        return models.Friendship.objects.filter(Q(initiator=user) | Q(reciprocator=user))


class SendGiftRequestView(generics.CreateAPIView):
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [AllowAny]
    serializer_class = serializers.GiftRequestSerializer
    throttle_classes = [throttling.AnonRateThrottle, throttling.UserRateThrottle]

    queryset = models.GiftRequest.objects.all()
    
    @swagger_auto_schema(operation_id='createGiftRequest')
    def post(self, request, *args, **kwargs):
        try:

            treasure_pk = request.data.get('treasure') # This should get the PK
            treasure = models.Treasure.objects.get(pk=treasure_pk, user=request.user)

            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            gift_request = serializer.save(
                sender=request.user,
                recipient=models.BadRainbowzUser.objects.get(pk=request.data['recipient']),
                treasure=treasure
            )

            gift_request_message = models.Message.objects.create(
                sender=request.user,
                recipient=gift_request.recipient,
                content=request.data['message']
            )
            gift_request_message.content_object = gift_request
            gift_request_message.save()

            inbox_item = models.InboxItem.objects.create(user=gift_request.recipient, message=gift_request_message)
            inbox_item.save()

            gift_request.treasure.pending = True
            gift_request.treasure.save()

        except models.BadRainbowzUser.DoesNotExist:
            raise PermissionDenied("Recipient user does not exist.")
        except models.Treasure.DoesNotExist:
            raise ValidationError("Treasure with the provided ID does not exist.")

        return Response({'success': 'Gift request sent successfully.'}, status=status.HTTP_201_CREATED)


# Add line(s) to delete message as well when request object is deleted (2/22)
class GiftRequestDetailView(generics.RetrieveUpdateAPIView):
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [AllowAny]
    serializer_class = serializers.AcceptRejectGiftRequestSerializer
    throttle_classes = [throttling.AnonRateThrottle, throttling.UserRateThrottle]

    queryset = models.GiftRequest.objects.all()

    def get_object(self):
        gift_request_id = self.kwargs['item_view_id']
        return get_object_or_404(models.GiftRequest, id=gift_request_id)

    @swagger_auto_schema(operation_id="getGiftRequest", operation_description="Gets gift request.")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(operation_id="replyGiftRequest", operation_description="Updates is_rejected or is_accepted on gift request, changes user of treasure if accepted, deletes request either way.")
    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        accepted = request.data.get('is_accepted')
        rejected = request.data.get('is_rejected')

        if accepted is not None:
            user = request.user
            treasure = instance.treasure
            treasure.accept(recipient=user, message=request.data.get('message'))

            treasure.pending = False
            treasure.save()

            with transaction.atomic():
                instance.delete()


            return Response({'success': 'Gift request accepted successfully!'}, status=status.HTTP_200_OK)

        if rejected is not None:
            treasure = instance.treasure
            treasure.pending = False
            treasure.save()

            with transaction.atomic():
                instance.delete()

            return Response({'success': 'Gift request rejected successfully!'}, status=status.HTTP_200_OK)

        return Response({'error': 'You must provide either "is_accepted" or "is_rejected" field.'}, status=status.HTTP_400_BAD_REQUEST)
