from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()

# Create your models here.
class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    id_user = models.IntegerField()
    firstname = models.CharField(max_length=30)
    secondname = models.CharField(max_length=30)
    date_of_birth = models.DateField(auto_now=False, auto_now_add=False)
    gender = models.CharField(max_length=15)
    email = models.EmailField(max_length=254)
    phone = models.CharField(max_length=17)
    location = models.CharField(max_length=100, blank=True)
    post_index = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=100, blank=True)
    profileimg = models.ImageField(upload_to='profile_images', default='blank_profile_picture.png')

    def __str__(self):
        return self.user.username

class Event(models.Model):
    event_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user_id = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='events')
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    date = models.DateField(auto_now=False, auto_now_add=False)
    time = models.TimeField(blank=True, null=True)
    additional_text = models.CharField(max_length=1024, blank=True, null=True)

    def __str__(self):
        return self.title

class Wishlist(models.Model):
    list_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    title = models.CharField(max_length=150)
    created_by = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='lists')
    event_id = models.ForeignKey(Event, null=True, blank=True, on_delete=models.SET_NULL, related_name='lists')
    
    class Meta:
        unique_together = ('title', 'created_by')  # Уникальное ограничение по комбинации полей

    def __str__(self):
        return self.title

class Wish(models.Model):
    wish_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    list_id = models.ForeignKey(Wishlist, on_delete=models.CASCADE, related_name='items')
    user_id = models.ForeignKey(Profile, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    url = models.URLField(max_length=2048, blank=True)
    picture = models.ImageField(upload_to='wish_images', default='blank_wish.png')
    desire = models.IntegerField(default=1)
    is_booked = models.BooleanField(default=0)
    booked_by_phone = models.CharField(max_length=17, default=0)

class Friendrequest(models.Model):
    follower = models.ForeignKey(Profile, related_name='following', on_delete=models.CASCADE)
    user_followed = models.ForeignKey(Profile, related_name='followers', on_delete=models.CASCADE)

class Friendship(models.Model):
    user1 = models.ForeignKey(Profile, related_name='friend1', on_delete=models.CASCADE)
    user2 = models.ForeignKey(Profile, related_name='friend2', on_delete=models.CASCADE)


#class SharedWishlists(models.Model):
#    wishlist_id = models.ForeignKey(Wishlist, on_delete=models.CASCADE)
#    user_id = models.ForeignKey(Profile, on_delete=models.CASCADE)
