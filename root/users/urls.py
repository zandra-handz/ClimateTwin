from django.urls import path
from . import views

urlpatterns = [

    path('activate/<uid>/<token>', views.ActivateUser.as_view({'get': 'activation'}), name='activation'),
    path('collected-items/', views.CollectedItemsView.as_view(), name='collected-items'),
    path('collected-item/<int:pk>', views.CollectedItemView.as_view(), name='collected-item'),
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('edit-profile/<int:pk>', views.EditUserProfileView.as_view(), name='edit-profile'),
    path('settings/', views.UserSettingsView.as_view(), name='settings'),
    path('change-settings/<int:pk>', views.ChangeUserSettingsView.as_view(), name='change-settings'),
    path('visited-places/', views.UserVisitsView.as_view(), name='visited-places'),
    path('visited-place/<int:pk>', views.UserVisitView.as_view(), name='visited-place'),
    

] 