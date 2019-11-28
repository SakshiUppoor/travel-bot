from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import sys
from requests import get
from wit import Wit
from datetime import datetime

from django.shortcuts import redirect, render, HttpResponseRedirect
from django.urls import reverse
from .models import ChatMessage, Booking
from django.contrib.auth.models import User, auth
from django.contrib import messages
from .forms import ChatForm
from django.db.models import Q


# Create your views here.

access_token = 'LKIQJBYIABCEHZG6H7JSU2QPRZLB4AWD'
client = Wit(access_token=access_token)

booking = {}
current_Booking = Booking()


def createNewChatMessage(request, intent):
    bot, created = User.objects.get_or_create(
        username='bot',
        is_staff=True,
    )

    newChatMessage = ChatMessage()
    newChatMessage.to_user = request.user
    newChatMessage.from_user = bot
    if intent == 'greeting':
        if Booking.objects.filter(customer=request.user, completed=True):
            newChatMessage.text = 'If you would like to book again, give a command like: "Book a room at the Plaza Hotel."'
            newChatMessage.save()
        else:
            newChatMessage.text = 'Hey there! I\'m a travel bot! I\'ll help you book your room. Give a command like: "Book a room at the Plaza Hotel."'
            newChatMessage.save()
    elif intent == "completed":
        newChatMessage.text = "Completed!"
        newChatMessage.save()
        newChatMessage = ChatMessage()

    else:
        newChatMessage.text = intent
        newChatMessage.save()


def first_entity_value(entities):
    global booking
    for entity in {'intent', 'location', 'number', 'from', 'to', 'datetime'}:
        if entity not in entities:
            # return None
            pass
        elif entity == 'location' and 'resolved' in entities[entity][0]:
            val = entities[entity][0]['resolved']['values'][0]['name']
            booking['destination'] = val
        elif entity == 'datetime':
            if 'to' in entities['datetime'][0]['values'][0] or 'from' in entities['datetime'][0]['values'][0]:
                if 'to' in entities['datetime'][0]['values'][0]:
                    val = entities['datetime'][0]['values'][0]['to']['value']
                    booking['checkOutDate'] = datetime.strptime(
                        val, "%Y-%m-%dT00:00:00.000+05:30")
                if 'from' in entities['datetime'][0]['values'][0]:
                    val = entities['datetime'][0]['values'][0]['from']['value']
                    booking['checkInDate'] = datetime.strptime(
                        val, "%Y-%m-%dT00:00:00.000+05:30")
            else:
                val = entities['datetime'][0]['values'][0]['value']
                if 'checkInDate' in booking:
                    if datetime.strptime(val, "%Y-%m-%dT00:00:00.000+05:30").date() > booking['checkInDate']:
                        booking['checkOutDate'] = datetime.strptime(
                            val, "%Y-%m-%dT00:00:00.000+05:30").date()
                    else:
                        booking['checkOutDate'] = booking['checkInDate']
                        booking['checkInDate'] = datetime.strptime(
                            val, "%Y-%m-%dT00:00:00.000+05:30").date()
                elif 'checkOutDate' in booking:
                    if datetime.strptime(val, "%Y-%m-%dT00:00:00.000+05:30").date() < booking['checkOutDate']:
                        booking['checkInDate'] = datetime.strptime(
                            val, "%Y-%m-%dT00:00:00.000+05:30")
                    else:
                        booking['checkInDate'] = booking['checkOutDate']
                        booking['checkOutDate'] = datetime.strptime(
                            val, "%Y-%m-%dT00:00:00.000+05:30").date()

                else:
                    booking['checkInDate'] = datetime.strptime(
                        val, "%Y-%m-%dT00:00:00.000+05:30").date()
        elif entity == 'to':
            if 'to' in entities['datetime'][0]['values'][0]:
                val = entities['datetime'][0]['values'][0]['to']['value']
                booking['checkOutDate'] = datetime.strptime(
                    val, "%Y-%m-%dT00:00:00.000+05:30").date()
        elif entity == 'from':
            if 'from' in entities['datetime'][0]['values'][0]:
                val = entities['datetime'][0]['values'][0]['from']['value']
                booking['checkInDate'] = datetime.strptime(
                    val, "%Y-%m-%dT00:00:00.000+05:30").date()
        else:
            val = entities[entity][0]['value']
            if entity == 'location':
                booking['destination'] = val
            elif entity == 'number':
                booking['noOfRooms'] = val

    return booking


def handle_message(request, response):
    entities = response['entities']
    global booking
    global current_Booking
    booking = first_entity_value(entities)
    if 'destination' in booking:
        current_Booking.destination = booking['destination']
    if 'checkInDate' in booking:
        current_Booking.checkInDate = booking['checkInDate']
    if 'checkOutDate' in booking:
        current_Booking.checkOutDate = booking['checkOutDate']
    if 'noOfRooms' in booking:
        current_Booking.noOfRooms = booking['noOfRooms']
    current_Booking.save()

    if 'destination' not in booking:
        createNewChatMessage(request, "Great! Where would you like to stay?")
    elif 'checkInDate' not in booking:
        createNewChatMessage(
            request, "Cool! When would you like to check in?")
    elif 'checkOutDate' not in booking:
        createNewChatMessage(
            request, "Got it! When would you like to check out?")
    elif 'noOfRooms' not in booking:
        createNewChatMessage(
            request, "Awesome! How many rooms would you like to book?")
    else:
        createNewChatMessage(request, "completed")
        current_Booking.completed = True
        current_Booking.save()


def chat(request):

    if request.user.is_authenticated:
        bot, created = User.objects.get_or_create(
            username='bot',
            is_staff=True,
        )
        global booking
        global current_Booking
        current_Booking, created = Booking.objects.get_or_create(
            customer=request.user,
            completed=False
        )
        if created == True:
            createNewChatMessage(request, 'greeting')
            booking.clear()
        if current_Booking.destination != None:
            booking['destination'] = current_Booking.destination
        if current_Booking.checkInDate != None:
            booking['checkInDate'] = current_Booking.checkInDate
        if current_Booking.checkOutDate != None:
            booking['checkOutDate'] = current_Booking.checkOutDate
        if current_Booking.noOfRooms != 0:
            booking['noOfRooms'] = current_Booking.noOfRooms

        form = ChatForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data['text']
            newChatMessage = ChatMessage()
            newChatMessage.text = text
            newChatMessage.from_user = request.user
            newChatMessage.to_user = User.objects.get(username='bot')
            newChatMessage.save()
            resp = client.message(newChatMessage.text)
            handle_message(request, resp)
            return HttpResponseRedirect(reverse('conversation:chat'))
        else:
            chatMessages = ChatMessage.objects.filter(
                Q(from_user=request.user) | Q(to_user=request.user))
            form = ChatForm()
            context = {
                'form': form,
                'chats': chatMessages,
                'bookings': Booking.objects.filter(completed=True, customer=request.user).order_by('-id'),
            }
        return render(request, 'chat.html', context)
    else:
        return HttpResponseRedirect(reverse('conversation:user_login'))


def register(request):

    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 == password2:
            if User.objects.filter(username=username).exists():
                messages.info(request, 'Username Taken')
                return HttpResponseRedirect(reverse('conversation:register'))
            elif User.objects.filter(email=email).exists():
                messages.info(request, 'Email Taken')
                return HttpResponseRedirect(reverse('conversation:register'))
            else:
                user = User.objects.create_user(
                    username=username, email=email, password=password1)
                user.save()
                return HttpResponseRedirect(reverse('conversation:chat'))
        else:
            messages.info(request, 'Password not matching')
            return HttpResponseRedirect(reverse('conversation:register'))
        return redirect('../')

    else:
        return render(request, 'join.html')


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect(reverse('conversation:chat'))
        else:
            messages.info(request, 'Username or password incorrect')
            return redirect('conversation:user_login')
    else:
        return render(request, 'login.html')


def user_logout(request):
    auth.logout(request)
    return redirect(reverse('conversation:user_login'))
