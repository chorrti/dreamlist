from django.contrib import admin
from .models import Profile, Wishlist, Wish, Friendrequest, Friendship, Event

# Register your models here.
admin.site.register(Profile)
admin.site.register(Wishlist)
admin.site.register(Wish)
admin.site.register(Friendrequest)
admin.site.register(Friendship)
admin.site.register(Event)