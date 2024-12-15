from django.shortcuts import render, redirect, get_object_or_404 
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Profile, Wish, Wishlist, Friendrequest, Friendship, Event
from django.db.models import Q
from django.urls import reverse
import phonenumbers
from datetime import datetime
from itertools import chain
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
import uuid

def transform_date(date_str):
    # Словарь для перевода названий месяцев с русского на английский
    months = {
        "Января": "January",
        "Февраля": "February",
        "Марта": "March",
        "Апреля": "April",
        "Мая": "May",
        "Июня": "June",
        "Июля": "July",
        "Августа": "August",
        "Сентября": "September",
        "Октября": "October",
        "Ноября": "November",
        "Декабря": "December"
    }
    # Заменяем месяц на английский
    for ru_month, en_month in months.items():
        if ru_month in date_str:
            date_str = date_str.replace(ru_month, en_month)
            break
    # Парсим строку даты
    parsed_date = datetime.strptime(date_str, "%d %B %Y")
    # Форматируем дату в нужный формат
    formatted_date = parsed_date.strftime("%Y-%m-%d")
    return formatted_date

def im_crop_center(img, w, h, name):
    img_width, img_height = img.size
    left, right = (img_width - w) / 2, (img_width + w) / 2
    top, bottom = (img_height - h) / 2, (img_height + h) / 2
    left, top = round(max(0, left)), round(max(0, top))
    right, bottom = round(min(img_width, right)), round(min(img_height, bottom))
    cropped_img = img.crop((left, top, right, bottom))
    img_io = BytesIO()
    cropped_img.save(img_io, format='PNG')
    img_io.seek(0)
    return ContentFile(img_io.read(), name=name)

def is_valid_phone_number(phone):
    try:
        # Если номер начинается с "8", заменяем его на "+7"
        if phone.startswith('8'):
            phone = '+7' + phone[1:]
        # Парсинг номера телефона как номер России
        parsed_number = phonenumbers.parse(phone, "RU")
        # Проверка на корректность номера
        if phonenumbers.is_valid_number(parsed_number):
            # Формирование строки с парсированным номером в нужном формате
            formatted_number = '8' + str(parsed_number.national_number)
            
            # Возвращаем информацию о номере и сам номер в строковом формате
            return True, formatted_number
        else:
            return False, None
    except phonenumbers.NumberParseException:
        return False, None

def users_type(request, pk): 
    user_object = User.objects.get(username=pk)# определение просматриваемого пользователя
    user_profile = Profile.objects.get(user=user_object)

    current_object = User.objects.get(username=request.user)# определение текущего пользователя
    current_user = Profile.objects.get(user=current_object)
    #print(current_user, '- текущий юзер')
    #print(user_profile, '- владелец')
    if (user_profile == current_user):#совпадает ли страница, на которую заходит пользователь, с её владельцем
        return user_profile, current_user, True
    else: return user_profile, current_user, False


def index(request):
    if request.method == 'POST':
        return redirect(signup)
    return render(request, 'welcome.html')


def about(request):
    return render(request, 'about.html')

def howtouse(request): 
    return render(request, 'Userbook.html')


def signup(request):
    if request.method == 'POST':
        firstname = request.POST['firstname']
        secondname = request.POST['secondname']
        date_of_birth = request.POST['date_of_birth']
        sex = request.POST['gender']
        email = request.POST['email']
        phone = request.POST['phone']

        if (_ := is_valid_phone_number(phone)[0]): #??
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Аккаунт с такой почтой уже существует')
                return redirect('signup')
            elif User.objects.filter(username=phone).exists():
                messages.info(request, 'Аккаунт с таким номером телефона уже существует')
                return redirect('signup')
            else:
                user = User.objects.create_user(username=phone, email=email, password=phone)
                user.save()
            user_login = auth.authenticate(username=phone, email=email, password=phone)
            auth.login(request, user_login)
            user_model = User.objects.get(username=phone)
            new_profile = Profile.objects.create(user=user_model, id_user=user_model.id, firstname=firstname, secondname=secondname, date_of_birth=date_of_birth, gender=sex, email=email, phone=phone)
            new_profile.save()
            new_wishlist = Wishlist.objects.create(title='Основной список', created_by=new_profile)
            new_wishlist.save()
            return redirect('profile', pk=user_model.username)
        else:
            messages.info(request, 'Номер телефона введён неправильно')
            return redirect('signup')
    else:
        return render(request, 'SignupView.html')

def login(request):
    if request.method == 'POST':
        username = request.POST['phone_login']
        email = request.POST['email_login']
        user = auth.authenticate(username=username, email=email, password=username)
        if user:
            auth.login(request, user)
            return redirect('profile', pk=username)
        else:
            messages.info(request, 'Что-то пошло не так')
            return redirect('login')

    else:
        return render(request, 'LoginView.html')

@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    return redirect('login')

@login_required(login_url='login')
def profile(request, pk):
    user_profile, current_user, is_same = users_type(request, pk)
    user_wishes = Wish.objects.filter(user_id=user_profile)
    is_friend_request_sent_from_user_profile = None
    is_friend_request_sent_from_current_user = None
    is_friends = None
    if not is_same:
        is_friends = Friendship.objects.filter(Q(user1=current_user) | Q(user2=current_user)).exists()
        if not is_friends:
            is_friend_request_sent_from_user_profile = Friendrequest.objects.filter(follower=user_profile, user_followed=current_user).exists()
            if not is_friend_request_sent_from_user_profile:
                is_friend_request_sent_from_current_user = Friendrequest.objects.filter(follower=current_user, user_followed=user_profile).exists()

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'exit': 
            auth.logout(request)
            return redirect('login')
        elif action == 'settings': 
            return redirect('settings', user_profile)
        elif action == 'wishes':
            return redirect('wishes', user_profile)
        elif action == 'lists':
            return redirect('lists', user_profile)
        elif action == 'calendar':
            return redirect('calendar', user_profile)
        elif action == 'createevent':
            return redirect('createevent', user_profile)
        elif action == 'cwish':
            return redirect('createwish', user_profile)
        elif action == 'events_soon':
            return redirect('events', user_profile)
        elif action == 'profile':
            return redirect('profile', current_user)
        elif action == 'friends':
            return redirect('friends', user_profile)
        elif action == 'about':
            return redirect('howtouse')
        elif action == 'follow':
            follow(user_profile, current_user)
            return redirect('profile', user_profile)
        elif action == 'add_friend':
            add_friend_from_profile(current_user, pk)
            return redirect('profile', user_profile)
        elif action == 'remove_friend':
            remove_friend_from_profile(current_user, pk)
            return redirect('profile', user_profile)
    context = {
        'current_user': current_user,
        'user': user_profile,
        'is_friend_request_sent': is_friend_request_sent_from_current_user,
        'is_friend_request_sent_by_profile': is_friend_request_sent_from_user_profile,
        'is_friends': is_friends}
    return render(request, 'ProfileView.html', context)

@login_required(login_url='login')
def wishes(request, pk):
    user_profile, current_user, is_same = users_type(request, pk)
    if (is_same):
        if request.method == 'POST':
            action = request.POST.get('action')
            if action == 'createevent':
                return redirect('createevent', user_profile)
            elif action == 'cwish':
                return redirect('createwish', user_profile)
            elif action == 'profile':
                return redirect('profile', current_user)
            elif action == 'createwish': 
                return redirect('createwish', current_user)
        main_list = Wishlist.objects.get(created_by=user_profile, title='Основной список')
        wishes = Wish.objects.filter(user_id=user_profile, list_id=main_list)
        context = {
            'items': wishes,
            'current_user': user_profile,
            'is_same_user': is_same
        }
        return render(request, 'WishlistView.html', context)
    else:
        return redirect('profile', current_user)


@login_required(login_url='login')
def lists(request, pk): 
    user_profile, current_user, is_same = users_type(request, pk)
    if (is_same):
        if request.method == 'POST':
            action = request.POST.get('action')
            if action == 'createevent':
                return redirect('createevent', user_profile)
            elif action == 'cwish':
                return redirect('createwish', user_profile)
            elif action == 'createlist':
                return redirect('createlist', user_profile)
            elif action == 'profile':
                return redirect('profile', current_user)
            else:
                list_id = request.POST.get('action')
                return redirect('list_detail', list=list_id, pk=pk)
            #return redirect('list_detail', Wishlist.objects.get(list_id=list_id))
            
        query_lists = Wishlist.objects.filter(created_by=user_profile)
        lists = []
        for i in query_lists:
            lists.append(i)
        context = {
            'lists': lists,
            'current_user': user_profile
        }
        return render(request, 'ListsView.html', context)
    else:
        return redirect('profile', current_user)


@login_required(login_url='login')
def list_detail(request, list, pk):
    user_profile, current_user, is_same = users_type(request, pk)
    if (is_same):
        if request.method == 'POST':
            action = request.POST.get('action')
            if action == 'profile': 
                return redirect('profile', user_profile)
            elif action == 'cwish': 
                return redirect('createwish', user_profile)
            elif action == 'createevent': 
                return redirect('createevent', user_profile)
            elif action == 'createwish': 
                return redirect('createwish', current_user)
        list_obj = Wishlist.objects.get(list_id=list)
        wishes = Wish.objects.filter(user_id=user_profile, list_id=list_obj)
        context = {
            'items': wishes,
            'current_user': user_profile,
            'is_same_user': is_same,
            'list': list_obj
        }
        return render(request, 'ListdetailsView.html', context)
    else:
        return redirect('profile', current_user)



@login_required(login_url='login')
def settings(request, pk):
    user_profile, current_user, is_same = users_type(request, pk)
    if (is_same):
        
        if request.method == 'POST':
            action = request.POST.get('action')
            if action == 'profile': 
                return redirect('profile', user_profile)
            elif action == 'cwish': 
                return redirect('createwish', user_profile)
            elif action == 'createevent': 
                return redirect('createevent', user_profile)
            elif action == 'cancel':
                return redirect('profile', user_profile)
            elif action == 'delete-account':
                user_to_delete = User.objects.get(username=user_profile.phone)
                user_profile.delete()
                user_to_delete.delete()
                return redirect('logout')
            elif action == 'save':
                if request.FILES.get('profileimg') != None:
                    image = request.FILES.get('profileimg')
                    img = Image.open(image)
                    width, height = img.size
                    if width > height:
                        image = im_crop_center(img, height, height, image.name)
                    else:
                        image = im_crop_center(img, width, width, image.name)
                    user_profile.profileimg.delete()
                else: 
                    image = user_profile.profileimg  
                firstname = request.POST['firstname']
                secondname = request.POST['secondname']
                post_index = request.POST['post_index']
                status = request.POST['status']
                location = request.POST['location']
                user_profile.profileimg = image
                user_profile.status = status
                user_profile.location = location
                user_profile.firstname = firstname
                user_profile.secondname = secondname
                user_profile.post_index = post_index
                user_profile.save()
                return redirect('profile', user_profile)
        return render(request, 'SettingsView.html', {'user': user_profile})
    else: return redirect('profile', current_user)

@login_required(login_url='login')
def events(request, pk): 
    user_profile, current_user, is_same = users_type(request, pk)
    if (is_same):
        if request.method == 'POST':
            action = request.POST.get('action')
            if action == 'profile': 
                return redirect('profile', user_profile)
            elif action == 'wishes': 
                return redirect('createwish', user_profile)
            elif action == 'calendar': 
                return redirect('calendar', user_profile)
            elif action == 'createevent': 
                return redirect('createevent', user_profile)
            if uuid.UUID(action):
                try:
                    wishlist = Wishlist.objects.get(event_id=uuid.UUID(action))
                    return redirect('eventlist_detail', list_name=wishlist.list_id, pk=pk)
                except Wishlist.DoesNotExist:
                    messages.info(request, 'К сожалению, у этого события нет списка!')
                    return redirect('events', pk=pk)
                

        events = []
        my_lists = Wishlist.objects.filter(created_by=user_profile, event_id__isnull=False)
        friends_profiles = []
        for i in Friendship.objects.filter(Q(user1=user_profile) | Q(user2=user_profile)):
            if i.user1 == user_profile:
                friends_profiles.append(i.user2)
            else:
                friends_profiles.append(i.user1)
        
        query_events = Event.objects.filter(user_id=user_profile)
        friends_events = Event.objects.filter(user_id__in=friends_profiles)
        combined_events = list(chain(query_events, friends_events))
        sorted_events = sorted(combined_events, key=lambda event: event.date)
        
        for i in sorted_events:
            events.append(i)
        
        wishlists_for_friends_events = []
        for event in friends_events:
            wishlists = Wishlist.objects.filter(event_id=event, created_by__in=friends_profiles, event_id__isnull=False)
            wishlists_for_friends_events.extend(wishlists)
        combined_lists = list(chain(wishlists_for_friends_events, my_lists))
        list_ids = [wishlist.list_id for wishlist in combined_lists]

        context = {
            'events': events,
            'current_user': user_profile,
            'lists': combined_lists,
        }
        return render(request, 'EventsView.html', context)
    else:
        return redirect('profile', current_user)

@login_required(login_url='login')
def eventlist_detail(request, list_name, pk):
    user_profile, current_user, is_same = users_type(request, pk)
    wishlist = Wishlist.objects.get(list_id=list_name)
    items = Wish.objects.filter(list_id=list_name)
    if request.method == 'POST':
            
            action = request.POST.get('action')
            if action == 'profile': 
                return redirect('profile', current_user)
            elif action == 'wishes': 
                return redirect('createwish', current_user)
            elif action == 'calendar': 
                return redirect('calendar', current_user)
            elif action == 'createwish': 
                return redirect('createwish', current_user)
            else:
                itemid = request.POST.get('modalId')
                is_booked = request.POST.get('ischecked', '0')
                booked_by = current_user.phone
                wish = Wish.objects.get(wish_id=itemid)
                wish.is_booked=is_booked
                wish.booked_by_phone = booked_by
                print(wish.booked_by_phone)
                wish.save()
    
    return render(request, 'EventlistdetailsView.html', {'list': wishlist, 'items': items, 'is_same_user': is_same})


@login_required(login_url='login')
def delete_list(request, list_id, pk):
    user_profile, current_user, is_same = users_type(request, pk)
    if is_same:
        list_delete = Wishlist.objects.get(list_id=list_id)
        list_delete.delete()
        return redirect('lists', user_profile)

@login_required(login_url='login')
def delete_wish(request, wish_id, pk):
    user_profile, current_user, is_same = users_type(request, pk)
    if is_same:
        wish = Wish.objects.get(wish_id=wish_id)
        wish.delete()
        return redirect('lists', user_profile)


@login_required(login_url='login')
def delete_event(request, event_id, pk):
    user_profile, current_user, is_same = users_type(request, pk)
    if is_same:
        event = Event.objects.get(event_id=event_id)
        event.delete()
        return redirect('events', user_profile)



@login_required(login_url='login')
def calendar(request, pk):
    user_profile, current_user, is_same = users_type(request, pk)
    if (is_same):
        if request.method == 'POST':
            action = request.POST.get('action')
            if action == 'add_event':
                chosen_date = request.POST.get('span_data')
                date = transform_date(chosen_date)
                url = reverse('createevent', args=[pk]) + f'?event_date={date}'
                return redirect(url)
            elif action == 'profile': 
                return redirect('profile', user_profile)
            elif action == 'cwish': 
                return redirect('createwish', user_profile)
            elif action == 'createevent': 
                return redirect('createevent', user_profile)
        return render(request, 'CalendarView.html')
    else: return redirect('profile', current_user)

@login_required(login_url='login')
def createevent(request, pk):
    user_profile, current_user, is_same = users_type(request, pk)
    event_date = request.GET.get('event_date')
    if (is_same):
        if request.method == 'POST':
            
            action = request.POST.get('action')
            if action == 'profile': 
                return redirect('profile', current_user)
            elif action == 'wishes': 
                return redirect('createwish', current_user)
            elif action == 'calendar': 
                return redirect('calendar', current_user)
            elif action == 'createwish': 
                return redirect('createwish', current_user)
            elif action == 'cancel': 
                return redirect('events', user_profile)
            elif action == 'save':
                if request.POST['title'] == '':
                    messages.info(request, 'Отсутствует название!')
                    return redirect('createevent', user_profile)
                elif request.POST['event_date'] == '':
                    messages.info(request, 'Отсутствует дата события!')
                    return redirect('createevent', user_profile)
                else:
                    is_list = False
                    create_list_checked = 'create_list' in request.POST
                    if create_list_checked:
                        if (Wishlist.objects.filter(title=request.POST['title'], created_by=user_profile).exists()):
                            messages.info(request, 'У вас уже есть список с таким названием, придумайте что-то другое или отмените создание списка')
                            return redirect('createevent', user_profile)
                        
                        else:
                            is_list = True
                    title = request.POST['title']
                    additional_text = request.POST['additional']
                    description = request.POST['description']
                    date = event_date if event_date else request.POST['event_date']
                    time = request.POST['event_time']
                    if time == '': time = None 
                    
                    new_event = Event.objects.create(user_id=user_profile, title=title, description=description, date=date, time=time, additional_text=additional_text)
                    new_event.save()
                    if is_list:
                        new_list = Wishlist(title=title, created_by=user_profile, event_id=new_event)
                        new_list.save()
                    return redirect('events', user_profile)
        else:
            lists = Wishlist.objects.filter(created_by=user_profile)
            return render(request, 'CreateeventView.html', {'items': lists, 'event_date': event_date})
    else:
        return redirect('profile', current_user)






@login_required(login_url='login')
def createwish(request, pk):
    user_profile, current_user, is_same = users_type(request, pk)
    if (is_same):
        if request.method == 'POST':
            action = request.POST.get('action')

            if action == 'profile': 
                return redirect('profile', current_user)
            elif action == 'wishes': 
                return redirect('createwish', current_user)
            elif action == 'calendar': 
                return redirect('calendar', current_user)
            elif action == 'createwish': 
                return redirect('createwish', current_user)
            elif action == 'cancel': 
                return redirect('wishes', user_profile)
            elif action == 'save':
                if request.POST['title'] == '':
                    messages.info(request, 'Отсутствует название!')
                    return redirect('createwish', user_profile)
                else:
                    title = request.POST['title']
                    description = request.POST['description']
                    url = request.POST['url']
                    desire = request.POST['desire']
                    list = request.POST['selected_item']
                    list_name = Wishlist.objects.get(created_by=user_profile, list_id=list)
                    list_instance = Wishlist.objects.get(created_by=user_profile, title=list_name)
                    
                    if request.FILES.get('picture') != None:
                        image = request.FILES.get('picture')
                        img = Image.open(image)
                        width, height = img.size
                        if width > height:
                            image = im_crop_center(img, height, height, image.name)
                        else:
                            image = im_crop_center(img, width, width, image.name)
                        new_wish = Wish.objects.create(user_id=user_profile, list_id=list_instance, title=title, description=description, url=url, picture=image, desire=desire)
                        new_wish.save()
                    else: 
                        new_wish = Wish.objects.create(user_id=user_profile, list_id=list_instance, title=title, description=description, url=url, desire=desire)
                        new_wish.save()
                    
                    return redirect('wishes', user_profile)
        else:
            lists = Wishlist.objects.filter(created_by=user_profile)
            return render(request, 'CreatewishView.html', {'items': lists})
    else:
        return redirect('profile', current_user)
    
@login_required(login_url='login')
def createlist(request, pk):
    user_profile, current_user, is_same = users_type(request, pk)
    if (is_same):
        if request.method == 'POST':
            action = request.POST.get('action')
            if action == 'profile': 
                return redirect('profile', current_user)
            elif action == 'wishes': 
                return redirect('createwish', current_user)
            elif action == 'calendar': 
                return redirect('calendar', current_user)
            elif action == 'createwish': 
                return redirect('createwish', current_user)


            elif action == 'cancel': 
                return redirect('profile')
            elif action == 'save':
                if request.POST['title'] == '':
                    messages.info(request, 'Отсутствует название!')
                    return redirect('createlist', current_user)
                if (Wishlist.objects.filter(title=request.POST['title'], created_by=user_profile).exists()):
                    messages.info(request, 'У вас уже есть список с таким названием, придумайте что-то другое')
                    return redirect('createlist', current_user)
                else:
                    title = request.POST['title']
                    new_list = Wishlist(title=title, created_by=user_profile)
                    new_list.save()

                    return redirect('lists', user_profile)
        else:
            return render(request, 'CreatelistView.html')
    else:
        return redirect('profile', current_user)

@login_required(login_url='login')
def friends(request, pk):
    user_profile, current_user, is_same = users_type(request, pk)
    if (is_same):
        if request.method == 'POST':
            action = request.POST.get('action')
            if action == 'profile': 
                return redirect('profile', user_profile)
            elif action == 'cwish': 
                return redirect('createwish', user_profile)
            elif action == 'createevent': 
                return redirect('createevent', user_profile)
        query_req = Friendrequest.objects.filter(user_followed=user_profile).values('follower')
        query_already_friends = Friendship.objects.filter(Q(user1=user_profile) | Q(user2=user_profile))
        query_outgoing = Friendrequest.objects.filter(follower=user_profile).values('user_followed')
        friendsrequest_profiles = []
        friends_profiles = []
        outgoing_requests = []
        for i in query_req:
            friendsrequest_profiles.append(Profile.objects.get(id=i['follower']))
        for i in query_outgoing:
            outgoing_requests.append(Profile.objects.get(id=i['user_followed']))
        for i in query_already_friends:
            if i.user1 == user_profile:
                friends_profiles.append(i.user2)
            else:
                friends_profiles.append(i.user1)
        context = {
            'user': user_profile,
            'incoming_requests': friendsrequest_profiles,
            'already_friends': friends_profiles,
            'outgoing_requests': outgoing_requests
        }
        return render(request, 'FriendsView.html', context)
    else:
        return redirect('profile', current_user)


@login_required(login_url='login')
def follow(user_profile, current_user):
    if Friendrequest.objects.filter(follower=current_user, user_followed=user_profile).exists():
        delete_follower = Friendrequest.objects.get(follower=current_user, user_followed=user_profile)
        delete_follower.delete()
        return redirect('profile', user_profile)
    else:
        new_follower = Friendrequest.objects.create(follower=current_user, user_followed=user_profile)
        new_follower.save()
        return redirect('profile', user_profile)

@login_required(login_url='login')
def unfollow(request, pk):
    user_profile, current_user, is_same = users_type(request, pk)
    if request.method == 'POST':
        phone = request.POST.get('phone')
        deleting_request = Friendrequest.objects.get(follower=user_profile, user_followed=Profile.objects.get(phone=phone))
        deleting_request.delete()
        return redirect('friends', user_profile)


#со страницы друзья
@login_required(login_url='login')
def remove_friend(request, pk):
    user_profile, current_user, is_same = users_type(request, pk)
    if request.method == 'POST':
        phone = request.POST.get('phone')
        deleting_user = Profile.objects.get(phone=phone)#
        delete_friendship = Friendship.objects.filter(Q(user1=user_profile, user2=deleting_user) | Q(user1=deleting_user, user2=user_profile))
        delete_friendship.delete()
        follow(user_profile, deleting_user)
        return redirect('friends', user_profile)


@login_required(login_url='login')
def add_friend(request, pk):
    user_profile, current_user, is_same = users_type(request, pk)
    if request.method == 'POST':
        phone = request.POST.get('phone')
        adding_user = Profile.objects.get(phone=phone)
        new_friendship = Friendship.objects.create(user1=user_profile, user2=adding_user)
        new_friendship.save()
        delete_follower = Friendrequest.objects.get(follower=adding_user, user_followed=user_profile)
        delete_follower.delete()
        return redirect('friends', user_profile)

#со страницы профиля (да, тупые макароны, но пусть пока будет так)
@login_required(login_url='login')
def add_friend_from_profile(user_profile, current_user):
    new_friendship = Friendship.objects.create(user1=Profile.objects.get(phone=user_profile), user2=Profile.objects.get(phone=current_user))
    new_friendship.save()
    delete_follower = Friendrequest.objects.get(follower=Profile.objects.get(phone=current_user), user_followed=Profile.objects.get(phone=user_profile))
    delete_follower.delete()
    return redirect('profile', user_profile)


@login_required(login_url='login')
def remove_friend_from_profile(user_profile, current_user):
    delete_friendship = Friendship.objects.filter(Q(user1=Profile.objects.get(phone=user_profile), user2=Profile.objects.get(phone=current_user)) | Q(user1=Profile.objects.get(phone=current_user), user2=Profile.objects.get(phone=user_profile)))
    delete_friendship.delete()
    follow(Profile.objects.get(phone=user_profile), Profile.objects.get(phone=current_user))
    return redirect('profile', current_user)