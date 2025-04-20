from . import models
from . import serializers
from climatevisitor.tasks.tasks import send_gift_notification, send_gift_accepted_notification, send_clear_gift_notification, send_friend_request_notification, send_friend_request_accepted_notification, send_clear_friend_request_notification, send_clear_notification_cache

from django.core.exceptions import ValidationError, PermissionDenied 
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import update_session_auth_hash
from django.db import transaction
from django.db.models import Q, Prefetch
from django_filters.rest_framework import DjangoFilterBackend # for user search
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render
 

from djoser.views import UserViewSet
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, filters, status, throttling, viewsets # filters is for user search
from rest_framework.authentication import SessionAuthentication, TokenAuthentication 
from rest_framework.decorators import api_view, authentication_classes, permission_classes, throttle_classes
from rest_framework.exceptions import PermissionDenied, MethodNotAllowed
from rest_framework.pagination import PageNumberPagination # for user search
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from rest_framework_simplejwt.authentication import JWTAuthentication

from rest_framework.views import APIView 
from django.views.decorators.csrf import csrf_exempt


import logging

logger = logging.getLogger(__name__)

class UserSearchPagination(PageNumberPagination):
    page_size = 10  
    page_size_query_param = 'page_size'
    max_page_size = 100


class CreateUserView(generics.CreateAPIView):

    queryset = models.BadRainbowzUser.objects.all()
    serializer_class = serializers.BadRainbowzUserSerializer
    permission_classes = [AllowAny]


class DeleteUserView(generics.DestroyAPIView):
 
    authentication_classes = [TokenAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated] 
    # No serializer class needed for just deleting 
    throttle_classes = [throttling.AnonRateThrottle, throttling.UserRateThrottle]

    def get_object(self):
        return self.request.user 

class ListUsersView(generics.ListAPIView):
    authentication_classes = [TokenAuthentication, JWTAuthentication] 
    queryset = models.BadRainbowzUser.objects.all()
    serializer_class = serializers.BadRainbowzUserSerializer
    permission_classes = [IsAuthenticated] 


# /api/users/?search=johndoe
class SearchUsersView(generics.ListAPIView):
    pagination_class = UserSearchPagination
    authentication_classes = [TokenAuthentication, JWTAuthentication] 
    queryset = models.BadRainbowzUser.objects.all()
    serializer_class = serializers.BadRainbowzUserSerializer
    permission_classes = [IsAuthenticated] 
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['username', 'email'] 

    

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


# @swagger_auto_schema(operation_id='resetUsername')
# class UsernameReset(UserViewSet):
#     pass


# @swagger_auto_schema(operation_id='resetPassword')
# class PasswordReset(UserViewSet):
#     pass



class RequestPasswordResetCodeView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        if not email:
            return Response({"detail": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = models.BadRainbowzUser.objects.get(email=email)
        except models.BadRainbowzUser.DoesNotExist:
            # Do not disclose if the email exists to prevent user enumeration
            return Response({"detail": "If the email exists, a reset code has been sent."}, status=status.HTTP_200_OK)

        # Generate and save the reset code
        reset_code = user.generate_password_reset_code()

        # Send the reset code via email
        send_mail(
            subject="Your Password Reset Code",
            message=f"Your password reset code is: {reset_code}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )

        return Response({"detail": "If the email exists, a reset code has been sent."}, status=status.HTTP_200_OK)


class PasswordResetCodeValidationView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = serializers.PasswordResetCodeValidationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
         
        validated_data = serializer.validated_data
         
        return Response({
            "detail": "Reset code and email are valid.",
            "email": validated_data['email'],
            "reset_code": validated_data['reset_code']
        }, status=status.HTTP_200_OK)



class PasswordResetConfirmView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = serializers.PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data
        serializer.save(user, request.data.get('new_password'))

        return Response({"detail": "Password has been reset successfully."}, status=status.HTTP_200_OK)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = serializers.ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = request.user
            old_password = serializer.validated_data['old_password']
            new_password = serializer.validated_data['new_password']
            
            # Change the password
            user.set_password(new_password)
            user.save()

            # Update the session authentication hash to avoid the user being logged out
            update_session_auth_hash(request, user)

            return Response({"detail": "Password updated successfully."}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@csrf_exempt
@authentication_classes([TokenAuthentication, JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_current_user(request):
    if not request.user.is_authenticated:
        return Response({'error': 'User not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
    
    serializer = serializers.BadRainbowzUserSerializer(request.user)
    return JsonResponse(serializer.data)

@api_view(['POST']) 
@authentication_classes([TokenAuthentication, JWTAuthentication])
@permission_classes([IsAuthenticated])
def clear_notification_cache(request):

    if request.method == 'POST':
        user = request.user 
 

        if user: 
            send_clear_notification_cache(user.id)
          
            return Response({'success': 'Request to send cache clearing task sent!'}, status=status.HTTP_200_OK)
        

        return Response({'error': 'User not found'}, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({'error': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


  

class TreasuresView(generics.ListCreateAPIView):
    authentication_classes = [TokenAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]
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
    authentication_classes = [TokenAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.TreasureSerializer
    throttle_classes = [throttling.AnonRateThrottle, throttling.UserRateThrottle]

    @swagger_auto_schema(operation_id='getUserTreasure', operation_description="Returns treasure.")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(operation_id='deleteUserTreasure', operation_description="Deletes treasure.")
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

    def get_queryset(self):
        return models.Treasure.objects.all()  # return all, ownership check happens below

    def perform_destroy(self, instance):
        if instance.finder != self.request.user:
            raise PermissionDenied("You are not allowed to delete this treasure.")
        instance.delete()

# MODEL DOESN'T EXIST, I am just using the treasure itself to get the records and store summary
# class TreasureHistoryOverView(generics.RetrieveAPIView):
#     authentication_classes = [TokenAuthentication, JWTAuthentication]
#     permission_classes = [IsAuthenticated]
#     serializer_class = serializers.TreasureHistorySerializer
#     throttle_classes = [throttling.AnonRateThrottle, throttling.UserRateThrottle]
#     queryset = models.TreasureHistory.objects.all()
#    #  lookup_field = 'treasure_id'  #  don't NEED to because DRF sees the pk in the path

#     @swagger_auto_schema(operation_id='viewTreasureHistoryOverView', operation_description="Gets a treasure's history overview.")
#     def get(self, request, *args, **kwargs):
#         return super().get(request, *args, **kwargs)
    
class TreasureOwnerChangeRecordsView(generics.ListCreateAPIView):
    authentication_classes = [TokenAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.TreasureOwnerChangeRecordSerializer
    throttle_classes = [throttling.AnonRateThrottle, throttling.UserRateThrottle]

    @swagger_auto_schema(operation_id='listTreasureOwnerChanges', operation_description="Returns owner changes for treasure.")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @swagger_auto_schema(operation_id='createTreasureOwnerChange', auto_schema=None)
    def post(self, request, *args, **kwargs):
        raise MethodNotAllowed('POST')

    def get_queryset(self):
        treasure_id = self.kwargs.get('treasure_id')
        return models.TreasureOwnerChangeRecord.objects.filter(treasure_id=treasure_id)


class TreasureOwnerChangeRecordView(generics.RetrieveAPIView):
    authentication_classes = [TokenAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.TreasureOwnerChangeRecordSerializer
    throttle_classes = [throttling.AnonRateThrottle, throttling.UserRateThrottle]
    queryset = models.TreasureOwnerChangeRecord.objects.all()
   #  lookup_field = 'treasure_id'  #  don't NEED to because DRF sees the pk in the path

    @swagger_auto_schema(operation_id='viewTreasureOwnerChangeRecord', operation_description="Gets an owner change record.")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
class UserPublicProfileView(generics.ListAPIView):
    authentication_classes = [TokenAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.UserProfileSerializer
    throttle_classes = [throttling.AnonRateThrottle, throttling.UserRateThrottle]

    @swagger_auto_schema(operation_id='getUserPublicProfile', operation_description="Returns user's public profile.")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    def get_queryset(self):
            user_id = self.kwargs.get('user_id')  
            return models.UserProfile.objects.filter(user__id=user_id)
        

class UserProfileView(generics.RetrieveUpdateAPIView):
    authentication_classes = [TokenAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.UserProfileSerializer
    throttle_classes = [throttling.AnonRateThrottle, throttling.UserRateThrottle]

    @swagger_auto_schema(operation_id='getUserProfile', operation_description="Returns user profile.")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(operation_id='updateUserProfile', operation_description="Updates user profile.")
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    def get_object(self):
        return (
            models.UserProfile.objects
            .select_related('user')
            .prefetch_related(
                Prefetch(
                    'user__visits',
                    queryset=models.UserVisit.objects.order_by('-visit_created_on')
                )
            )
            .get(user=self.request.user)
        )
    
class UpdateUserProfileView(generics.RetrieveUpdateAPIView, generics.DestroyAPIView):
    authentication_classes = [TokenAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.UpdateUserProfileSerializer
    throttle_classes = [throttling.AnonRateThrottle, throttling.UserRateThrottle]


    @swagger_auto_schema(operation_id='getUserProfileToEdit', operation_description="Returns user profile in edit view.")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(operation_id='updateUserProfile', operation_description="Updates user profile.")
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(operation_id='partialUpdateUserProfile', operation_description="Updates user profile via PATCH.", auto_schema=None)
    def patch(self, request, *args, **kwargs): 
        return super().partial_update(request, *args, **kwargs)  
    
    @swagger_auto_schema(operation_id='deleteUserProfile', operation_description="Deletes user profile.", auto_schema=None)
    def delete(self, request, *args, **kwargs):
        raise MethodNotAllowed('DELETE')

    def get_queryset(self):
        return models.UserProfile.objects.filter(user=self.request.user)



# if this works well and does optimize,
class UserSettingsView(generics.RetrieveUpdateAPIView):
    """
    Efficiently retrieve and update the authenticated user's settings.
    """
    authentication_classes = [TokenAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.UserSettingsSerializer
    throttle_classes = [throttling.AnonRateThrottle, throttling.UserRateThrottle]

    @swagger_auto_schema(operation_id='getUserSettings', operation_description="Returns user settings.")
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(operation_id='updateUserSettings', operation_description="Updates user settings.")
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def get_object(self):
        # Retrieves the settings instance for the authenticated user
        return models.UserSettings.objects.get(user=self.request.user)
    
    
# class UserSettingsView(generics.ListCreateAPIView):
#     authentication_classes = [TokenAuthentication, JWTAuthentication]
#     permission_classes = [IsAuthenticated]
#     serializer_class = serializers.UserSettingsSerializer
#     throttle_classes = [throttling.AnonRateThrottle, throttling.UserRateThrottle]

#     @swagger_auto_schema(operation_id='createUserSettings', operation_description="Creates user settings.")
#     def post(self, request, *args, **kwargs):
#         return super().post(request, *args, **kwargs)

#     @swagger_auto_schema(operation_id='getUserSettings', operation_description="Returns user settings.")
#     def get(self, request, *args, **kwargs):
#         return super().get(request, *args, **kwargs)

#     def get_queryset(self):
#         return models.UserSettings.objects.filter(user=self.request.user)


class ChangeUserSettingsView(generics.RetrieveUpdateAPIView):
    authentication_classes = [TokenAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.UserSettingsSerializer
    throttle_classes = [throttling.AnonRateThrottle, throttling.UserRateThrottle]

    @swagger_auto_schema(operation_id='getUserSettingsToChange', operation_description="Returns user settings in change view.")
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
    authentication_classes = [TokenAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.UserVisitSerializer
    throttle_classes = [throttling.AnonRateThrottle, throttling.UserRateThrottle]

    @swagger_auto_schema(operation_id='listUserVisits', operation_description="Returns user visits.")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    def get_queryset(self):
        return models.UserVisit.objects.filter(user=self.request.user)
    

class UserVisitView(generics.RetrieveAPIView, generics.DestroyAPIView):
    authentication_classes = [TokenAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]
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
    authentication_classes = [TokenAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.InboxSerializer
    throttle_classes = [throttling.AnonRateThrottle, throttling.UserRateThrottle]

 

    @swagger_auto_schema(operation_id='getInboxItems', operation_description="Returns inbox items.")
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = serializers.InboxItemSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # prefetches based on serializer; I don't entirely understand how this works or how well, yet
    def get_queryset(self):
        return (
            models.InboxItem.objects
            .filter(user=self.request.user)
            .select_related(
                'message',
                'message__sender',
                'message__content_type'  
            )
        )

class InboxItemDetailView(generics.RetrieveDestroyAPIView):
    authentication_classes = [TokenAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]
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
    authentication_classes = [TokenAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]
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
    authentication_classes = [TokenAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.MessageSerializer 
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


class SendFriendRequestView(generics.CreateAPIView):
    authentication_classes = [TokenAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.FriendRequestSerializer
    throttle_classes = [throttling.AnonRateThrottle, throttling.UserRateThrottle]

    queryset = models.FriendRequest.objects.all()

    @swagger_auto_schema(operation_id='createFriendRequest')
    def post(self, request, *args, **kwargs):
        sender = self.request.user
        message = self.request.data.get('message')

        try:
            recipient_id = request.data.get('recipient')
            if not isinstance(recipient_id, int):  # Check if recipient_id is a valid integer
                raise TypeError("Invalid recipient ID. Expected an integer.")

            recipient = models.BadRainbowzUser.objects.get(pk=recipient_id)
        except models.BadRainbowzUser.DoesNotExist:
            return Response({"error": "Recipient user does not exist."}, status=status.HTTP_404_NOT_FOUND)
        except TypeError as e:
            logger.error(f"TypeError: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return Response({"error": "An unexpected error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        existing_request = models.FriendRequest.objects.filter(sender=request.user, recipient=recipient)
        if existing_request.exists():
            return Response({'error': 'Friend request already sent.'}, status=status.HTTP_400_BAD_REQUEST)

        existing_friendship = models.Friendship.objects.filter(initiator=request.user, reciprocator=recipient)
        if existing_friendship.exists():
            return Response({'error': 'You are already friends with this person.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        friend_request = serializer.save(sender=request.user, recipient=recipient)

        friend_request_message = models.Message.objects.create(sender=request.user, recipient=recipient, content=message)
        friend_request_message.content_object = friend_request
        friend_request_message.save()

        inbox_item = models.InboxItem.objects.create(user=recipient, message=friend_request_message)
        inbox_item.save()

        logger.info("Calling send_friend_request_notification synchronously for testing...")
        send_friend_request_notification(request.user.id, request.user.username, recipient.id, inbox_item.id, friend_request.id)

        return Response({'success': 'Friend request sent successfully.'}, status=status.HTTP_201_CREATED)

class FriendRequestDetailView(generics.RetrieveUpdateAPIView):
    authentication_classes = [TokenAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]
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


        if accepted is not None and accepted == True:
            user = request.user
            friend = instance.sender
            friendship = models.Friendship.objects.create(initiator=friend, reciprocator=user)

            friend_friendship_profile = models.FriendProfile.objects.create(user=user, friend=friend, friendship=friendship)
            friend_friendship_profile.save()

            user_friendship_profile = models.FriendProfile.objects.create(user=friend, friend=user, friendship=friendship)
            user_friendship_profile.save()

            with transaction.atomic():
                instance.delete()


            logger.info("Calling send_friend_request_accepted_notification synchronously for testing...")
            send_friend_request_accepted_notification(request.user.id, request.user.username, friend.id)

                

            return Response({'success': 'Friend request accepted successfully!'}, status=status.HTTP_200_OK)
        
        elif rejected is not None: 

            user = request.user
            friend = instance.sender

            with transaction.atomic():
                instance.delete()

            logger.info("Calling send_clear_friend_request_notification synchronously for testing...")
            send_clear_friend_request_notification(user.id, friend.id)

            return Response({'success': 'Friend request rejected successfully!'}, status=status.HTTP_200_OK)

        return Response({'error': 'You must provide either "is_accepted" or "is_rejected" field.'}, status=status.HTTP_400_BAD_REQUEST)



    @swagger_auto_schema(operation_id="partialUpdateFriendRequest", operation_description="Updates friend request via PATCH", auto_schema=None)
    def patch(self, request, *args, **kwargs):
        raise MethodNotAllowed('PATCH')

        


class FriendProfilesView(generics.ListAPIView):
    authentication_classes = [TokenAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.FriendProfileSerializer
    throttle_classes = [throttling.AnonRateThrottle, throttling.UserRateThrottle]

    @swagger_auto_schema(operation_id='listFriendProfiles', operation_description="Returns friend profiles.")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    def get_queryset(self):
        return (
            models.FriendProfile.objects
            .filter(user=self.request.user)
            .select_related('friend', 'friend__profile', 'friend__profile__user')  # Optimizes FK lookups in serializer
        )

class FriendProfileView(generics.RetrieveUpdateAPIView):
    authentication_classes = [TokenAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]
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
    authentication_classes = [TokenAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.FriendshipSerializer
    throttle_classes = [throttling.AnonRateThrottle, throttling.UserRateThrottle]

    @swagger_auto_schema(operation_id='deleteFriendship', operation_description="Deletes friendship.")
    def delete(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        return models.Friendship.objects.filter(Q(initiator=user) | Q(reciprocator=user))


class SendGiftRequestView(generics.CreateAPIView):
    authentication_classes = [TokenAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]
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


            print(gift_request.recipient.id)
 
            send_gift_notification(request.user.id, request.user.username, gift_request.recipient.id, inbox_item.id, gift_request.id)

        

            gift_request.treasure.pending = True
            gift_request.treasure.save()

        except models.BadRainbowzUser.DoesNotExist:
            raise PermissionDenied("Recipient user does not exist.")
        except models.Treasure.DoesNotExist:
            raise ValidationError("Treasure with the provided ID does not exist.")

        return Response({'success': 'Gift request sent successfully.'}, status=status.HTTP_201_CREATED)


class SendGiftRequestBackToFinderView(generics.CreateAPIView):
    authentication_classes = [TokenAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.GiftRequestBackToFinderSerializer
    throttle_classes = [throttling.AnonRateThrottle, throttling.UserRateThrottle]

    queryset = models.GiftRequest.objects.all()

    @swagger_auto_schema(operation_id='createGiftBackToFinder')
    def post(self, request, *args, **kwargs):
        try:
            treasure_pk = request.data.get('treasure')
            treasure = models.Treasure.objects.get(pk=treasure_pk, user=request.user)
 
            if not treasure.finder or treasure.finder == request.user:
                raise ValidationError("This treasure cannot be sent -- either finder account does not exist, or you are the finder.")

            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            gift_request = serializer.save(
                sender=request.user,
                recipient=treasure.finder,  
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

            send_gift_notification(
                request.user.id,
                request.user.username,
                gift_request.recipient.id,
                inbox_item.id,
                gift_request.id
            )

            # Mark treasure as pending
            treasure.pending = True
            treasure.save(update_fields=["pending"])

        except models.Treasure.DoesNotExist:
            raise ValidationError("Treasure with the provided ID does not exist.")
        except Exception as e:
            raise ValidationError(str(e))

        return Response({'success': 'Gift request sent back to original finder successfully.'}, status=status.HTTP_201_CREATED)
    
# Add line(s) to delete message as well when request object is deleted (2/22)
class GiftRequestDetailView(generics.RetrieveUpdateAPIView):
    authentication_classes = [TokenAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]
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

            # Saving the record in here 
            treasure.accept(recipient=user, message=request.data.get('message'))

            treasure.pending = False
            treasure.save()

            with transaction.atomic():
                instance.delete()

            logger.info("Calling send_accepted_gift_notification synchronously for testing...")
            send_gift_accepted_notification(request.user.id, request.user.username, instance.sender.id)


            return Response({'success': 'Gift request accepted successfully!'}, status=status.HTTP_200_OK)

        if rejected is not None:
            treasure = instance.treasure
            treasure.pending = False
            treasure.save()

            with transaction.atomic():
                instance.delete()

            logger.info("Calling send_clear_gift_notification synchronously for testing...")
            send_clear_gift_notification(request.user.id, instance.sender.id)

            return Response({'success': 'Gift request rejected successfully!'}, status=status.HTTP_200_OK)

        return Response({'error': 'You must provide either "is_accepted" or "is_rejected" field.'}, status=status.HTTP_400_BAD_REQUEST)


class UserSummaryView(generics.ListAPIView):
    authentication_classes = [TokenAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.UserSummarySerializer
    throttle_classes = [throttling.AnonRateThrottle, throttling.UserRateThrottle]

    @swagger_auto_schema(operation_id='listUserSummary', operation_description="Returns user summary.")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    

    def get_queryset(self):
        return models.BadRainbowzUser.objects.filter(username=self.request.user.username)


class UserLinksView(generics.ListAPIView):
    authentication_classes = [TokenAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.UserLinksSerializer
    throttle_classes = [throttling.AnonRateThrottle, throttling.UserRateThrottle]

    @swagger_auto_schema(operation_id='listUserLinks', operation_description="Returns user links.")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    

    def get_queryset(self):
        return models.BadRainbowzUser.objects.filter(username=self.request.user.username)
    



@api_view(['POST'])
@throttle_classes([AnonRateThrottle, UserRateThrottle]) 
@authentication_classes([TokenAuthentication, JWTAuthentication])
@permission_classes([IsAuthenticated])
def clean_treasures_data(request):
    """
    View to update existing treasures to newer designs.
    """

    if request.method == 'OPTIONS':
        return Response(status=status.HTTP_200_OK)
    
    if request.method == 'POST':
        user = request.user 

        if not user or not user.is_superuser:
            return Response({'Error': 'Not authorized'}, status=status.HTTP_401_UNAUTHORIZED)
        
        all_treasures = models.Treasure.objects.all()

        if not all_treasures:
            return Response({'detail': 'No treasures to check'}, status=status.HTTP_200_OK)

        change_count = 0

        total_treasures = len(all_treasures)
        print(f'Total treasures in DB: {total_treasures}')

        for treasure in all_treasures:
            if treasure.finder is None and treasure.original_user is not None:
                username = treasure.original_user
                user_instance = models.BadRainbowzUser.objects.get(username=username)
                treasure.finder = user_instance
                treasure.save()
                print(f"Added finder for treasure {treasure.descriptor or 'No descriptor given'}")

                change_count += 1

        return Response({'detail': f'{change_count} treasures updated with current clean logic!'}, status=status.HTTP_200_OK)
 
    return Response({'Error': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)



