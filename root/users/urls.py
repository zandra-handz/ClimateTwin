from django.urls import path
from . import views

urlpatterns = [

    path('activate/<uid>/<token>', views.ActivateUser.as_view({'get': 'activation'}), name='activation'),
    path('username/reset/confirm/<uid>/<token>', views.UsernameReset.as_view({'get': 'reset_username'}), name='reset-username'),
    path('password/reset/confirm/<uid>/<token>', views.PasswordReset.as_view({'get': 'reset_password'}), name='reset=password'),
    path('treasures/', views.TreasuresView.as_view(), name='treasures'),
    path('treasure/<int:pk>', views.TreasureView.as_view(), name='treasure'),
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('edit-profile/<int:pk>', views.EditUserProfileView.as_view(), name='edit-profile'),
    path('settings/', views.UserSettingsView.as_view(), name='settings'),
    path('change-settings/<int:pk>', views.ChangeUserSettingsView.as_view(), name='change-settings'),
    path('visited-places/', views.UserVisitsView.as_view(), name='visited-places'),
    path('visited-place/<int:pk>', views.UserVisitView.as_view(), name='visited-place'),
    

] 