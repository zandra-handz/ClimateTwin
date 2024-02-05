from django.urls import path
from . import views

urlpatterns = [

    path('activate/<uid>/<token>', views.ActivateUser.as_view({'get': 'activation'}), name='activation'),
    path('username/reset/confirm/<uid>/<token>', views.UsernameReset.as_view({'get': 'reset_username'}), name='reset-username'),
    path('password/reset/confirm/<uid>/<token>', views.PasswordReset.as_view({'get': 'reset_password'}), name='reset-password'),
    path('treasures/', views.TreasuresView.as_view(), name='treasures'),
    path('treasure/<int:pk>', views.TreasureView.as_view(), name='treasure'),
    path('inbox/items/', views.InboxView.as_view(), name='inbox-list'),
    path('inbox/item/<int:pk>/', views.ItemDetailView.as_view(), name='inbox-item-detail'),
    path('inbox/accept-friend-request/<int:item_view_id>/', views.FriendRequestDetailView.as_view(), name='accept-friend-request'),
    path('inbox/accept-gift-request/<int:item_view_id>/', views.GiftRequestDetailView.as_view(), name='accept-gift-request'),
    path('messages/create/', views.CreateMessageView.as_view(), name='create_message'),
    path('messages/send/', views.send_message, name='send_message'),
    path('message/<int:pk>/', views.MessageView.as_view(), name='message-detail'),
    path('send-friend-request/', views.SendFriendRequestView.as_view(), name='send-friend-request'),
    path('send-gift-request/', views.SendGiftRequestView.as_view(), name='send-gift-request'),
    path('friends/', views.UserFriendshipsView.as_view(), name='friends'),
    path('friend/<int:pk>', views.UserFriendshipView.as_view(), name='friend'),
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('edit-profile/<int:pk>', views.EditUserProfileView.as_view(), name='edit-profile'),
    path('settings/', views.UserSettingsView.as_view(), name='settings'),
    path('change-settings/<int:pk>', views.ChangeUserSettingsView.as_view(), name='change-settings'),
    path('visited-places/', views.UserVisitsView.as_view(), name='visited-places'),
    path('visited-place/<int:pk>', views.UserVisitView.as_view(), name='visited-place'),
    

] 