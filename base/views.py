from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout 
from django.contrib.auth.forms import UserCreationForm
from .models import Room, Topic
from .forms import RoomForm

# Create your views here.

# ---------------------------------------------------
# Sample in-memory rooms list (not used anymore)
# Kept for learning/reference purposes
# ---------------------------------------------------
# rooms = [
#     {'id': 1, 'name':'Lets learn python'},
#     {'id': 2, 'name':'Design with me'},
#     {'id': 3, 'name':'Frontend developers'}
# ]


def loginPage(request):
    page = 'login'
    # If a user is already authenticated, redirect them to the home page
    if request.user.is_authenticated:
        return redirect('home')

    # Handle form submission when user tries to log in
    if request.method == 'POST':
        # Get username and password from POST request
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        # Check if the user exists in the database
        try:
            user = User.objects.get(username=username)
        except:
            # Display error message if user is not found
            messages.error(request, 'User does not exist')

        # Authenticate user credentials
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # Log the user in and start a session
            login(request, user)
            return redirect('home')
        else:
            # Display error message for invalid credentials
            messages.error(request, 'Username or password does not exist')

    # Context can be expanded later if needed
    context = {'page': page}
    return render(request, 'base/login_register.html', context)


def logoutUser(request):
    # Log out the currently authenticated user
    logout(request)
    return redirect('home')

def registerPage(request):
    # page = 'register'
    form = UserCreationForm

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            # Save the new user and log them in
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            # Display error messages for invalid form data
            messages.error(request, 'An error occurred during registration')    
    return render(request, 'base/login_register.html', {'form': form})


def home(request):
    # Get search query from URL parameters (?q=...)
    q = request.GET.get('q') if request.GET.get('q') != None else ''

    # Filter rooms by topic name, room name, or description
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    ).order_by('-updated', '-created')

    # Retrieve all topics
    topics = Topic.objects.all()

    # Count number of rooms returned
    room_count = rooms.count()

    # Data passed to the template
    context = {'rooms': rooms, 'topics': topics, 'room_count': room_count}
    return render(request, 'base/home.html', context)


def room(request, pk):
    # Retrieve a single room by primary key (id)
    room = Room.objects.get(id=pk)

    # Example logic using the in-memory rooms list (kept for reference)
    # room = None
    # for i in rooms:
    #     if i['id'] == int(pk):
    #         room = i

    # Pass room data to the template
    context = {'room': room}
    return render(request, 'base/room.html', context) 


@login_required(login_url='login')
def createRoom(request):
    # Initialize an empty form for creating a room
    form = RoomForm()

    # Handle form submission
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            # Save new room to the database
            form.save()
            return redirect('home')

    # Re-render the form if not submitted or invalid
    form = RoomForm()
    context = {'form': form}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login')
def updateRoom(request, pk):
    # Retrieve the room to be updated
    room = Room.objects.get(id=pk)

    # Populate the form with existing room data
    form = RoomForm(instance=room)

    # Prevent users who are not the room host from editing
    if request.user != room.host:
        return HttpResponse('Your are not allowed here!')

    # Handle form submission for updating the room
    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            # Save changes to the room
            form.save()
            return redirect('home')

    # Render the update form
    context = {'form': form}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login')
def deleteRoom(request, pk):
    # Retrieve the room to be deleted
    room = Room.objects.get(id=pk)

    # Ensure only the host can delete the room
    if request.user != room.host:
        return HttpResponse('Your are not allowed here!')

    # Delete room after confirmation
    if request.method == 'POST':
        room.delete()
        return redirect('home')

    # Render delete confirmation page
    return render(request, 'base/delete.html', {'obj': room})
