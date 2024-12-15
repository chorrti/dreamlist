from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about', views.about, name='about'),
    path('howtouse', views.howtouse, name='howtouse'),
    path('signup', views.signup, name='signup'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('profile/<str:pk>', views.profile, name='profile'),
    path('settings/<str:pk>', views.settings, name='settings'),
    path('wishes/<str:pk>', views.wishes, name='wishes'),
    path('events/<str:pk>', views.events, name='events'),
    path('createwish/<str:pk>', views.createwish, name='createwish'),
    path('createlist/<str:pk>', views.createlist, name='createlist'),
    path('createevent/<str:pk>', views.createevent, name='createevent'),
    path('delete_event/<uuid:event_id>/<str:pk>/', views.delete_event, name='delete_event'),
    path('delete_wish/<uuid:wish_id>/<str:pk>/', views.delete_wish, name='delete_wish'),
    path('delete_list/<uuid:list_id>/<str:pk>/', views.delete_list, name='delete_list'),
    path('lists/<str:pk>', views.lists, name='lists'),
    path('list_detail/<str:list>/<str:pk>', views.list_detail, name='list_detail'),
    path('eventlist_detail/<str:list_name>/<str:pk>', views.eventlist_detail, name='eventlist_detail'),    
    path('friends/<str:pk>', views.friends, name='friends'),
    path('add_friend/<str:pk>', views.add_friend, name='add_friend'),
    path('remove_friend/<str:pk>', views.remove_friend, name='remove_friend'),
    path('follow', views.follow, name='follow'),
    path('unfollow/<str:pk>', views.unfollow, name='unfollow'),
    path('remove_friend_from_profile', views.remove_friend_from_profile, name='remove_friend_from_profile'),
    path('add_friend_from_profile', views.add_friend_from_profile, name='add_friend_from_profile'),
    path('calendar/<str:pk>', views.calendar, name='calendar')
]