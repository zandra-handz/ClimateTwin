from django.urls import path
from . import views

urlpatterns = [


    path('get-current/', views.get_current_user, name='get-current-user'),
    path('get-all/', views.ListUsersView.as_view(), name='get-all-users'),
    path('get/', views.SearchUsersView.as_view(), name='search-users'), # /api/users/get/?search=johndoe
    path('sign-up/', views.CreateUserView.as_view(), name='sign_up'),
    path('send-reset-code/', views.RequestPasswordResetCodeView.as_view(), name='send-reset-code'),
    path('verify-reset-code/', views.PasswordResetCodeValidationView.as_view(), name='verify-reset-code'),
    path('reset-password/', views.PasswordResetConfirmView.as_view(), name='reset-password'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change-password'),
  
    # Old, not using?
    path('activate/<uid>/<token>', views.ActivateUser.as_view({'get': 'activation'}), name='activation'),
   
   # Old and perhaps never finished
    # path('username/reset/confirm/<uid>/<token>', views.UsernameReset.as_view({'get': 'reset_username'}), name='reset-username'),
    # path('password/reset/confirm/<uid>/<token>', views.PasswordReset.as_view({'get': 'reset_password'}), name='reset-password'),
    
    path('treasures/', views.TreasuresView.as_view(), name='treasures'),
    path('treasure/<int:pk>/', views.TreasureView.as_view(), name='treasure'),
    path('inbox/items/', views.InboxView.as_view(), name='inbox-list'),
    path('inbox/item/<int:pk>/', views.InboxItemDetailView.as_view(), name='inbox-item-detail'),
    path('inbox/accept-friend-request/<int:item_view_id>/', views.FriendRequestDetailView.as_view(), name='accept-friend-request'),
    path('inbox/accept-gift-request/<int:item_view_id>/', views.GiftRequestDetailView.as_view(), name='accept-gift-request'),
    path('clear-notification-cache/', views.clear_notification_cache, name='clear_notification_cache'),   
    path('messages/create/', views.CreateMessageView.as_view(), name='create_message'),
    path('messages/send/', views.send_message, name='send_message'),
    path('message/<int:pk>/', views.MessageView.as_view(), name='message-detail'),
    path('send-friend-request/', views.SendFriendRequestView.as_view(), name='send-friend-request'),
    path('send-gift-request/', views.SendGiftRequestView.as_view(), name='send-gift-request'),
    path('friends/', views.FriendProfilesView.as_view(), name='friends'),
    path('friend/<int:pk>/', views.FriendProfileView.as_view(), name='friend'),
    path('delete-friend/<int:pk>/', views.DeleteFriendshipView.as_view(), name='delete-friend'),
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('edit-profile/<int:pk>/', views.EditUserProfileView.as_view(), name='edit-profile'),
    path('settings/', views.UserSettingsView.as_view(), name='settings'),
    path('change-settings/<int:pk>/', views.ChangeUserSettingsView.as_view(), name='change-settings'),
    path('visited-places/', views.UserVisitsView.as_view(), name='visited-places'),
    path('visited-place/<int:pk>/', views.UserVisitView.as_view(), name='visited-place'),
    path('summary/', views.UserSummaryView.as_view(), name='summary'),
    path('links/', views.UserLinksView.as_view(), name='links'),
    

] 