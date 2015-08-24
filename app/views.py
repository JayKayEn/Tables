import json
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.cache import never_cache
from instagram.client import InstagramAPI
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from time import strftime, gmtime
from .keys import client_info
from .models import AccessToken, Person, Followees, Table
from .forms import NewTableForm, EditTableForm
from .serializers import PersonSerializer, TableSerializer, FolloweesSerializer

client_id = client_info['client_id']
client_secret = client_info['client_secret']
redirect_uri = client_info['redirect_uri']

api = InstagramAPI(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri)

def landing(request):
    if request.user.is_authenticated():
        try:
            person = Person.objects.get(profile=request.user.get_username())
            access_token = AccessToken.objects.get(user=request.user)
            request.session['access_token'] = access_token.value
            if 'updated' not in request.session:
                followees, created = Followees.objects.get_or_create(user=request.user)
                followees.update(api)
                tables = Table.objects.filter(user=request.user)
                # for table in tables:
                #     table.update()
                request.session['updated'] = True;
            else:
                print('exists')
            return redirect('app.views.user_home')
        except Person.DoesNotExist:
            return redirect('app.views.auth_info')
        except AccessToken.DoesNotExist:
            return redirect('app.views.auth_info')
    else:
        return render(request, 'landing.html')

@login_required(login_url='/login/')
def user_home(request):
    followees = Followees.objects.get(user=request.user).people.values()
    tables = Table.objects.filter(user=request.user).order_by('name')
    return render(request, "user_home.html", {'followees': followees, 'tables': tables})

@login_required(login_url='/login/')
def table_detail(request, pk):
    table = get_object_or_404(Table, pk=pk)
    people = table.people.values()
    return render(request, 'table_detail.html', {'table': table, 'people': people})

@login_required(login_url='/login/')
def table_new(request):
    if request.method == "POST":
        form = NewTableForm(request.POST)
        if form.is_valid():
            table = form.save(commit=False)
            table.user = request.user
            try:
                table.save()
                return redirect('app.views.table_edit', pk=table.pk)
            except IntegrityError:
                message = "A table with that name already exists."
                return render(request, 'table_new.html', {'form' : form, 'message': message})
    else:
        form = NewTableForm()
    return render(request, 'table_new.html', {'form' : form})

@login_required(login_url='/login/')
def table_edit(request, pk):
    if request.method == "POST":
        adds = None
        removes = None
        if 'adds[]' in request.POST:
            adds = request.POST.getlist('adds[]')
        if 'removes[]' in request.POST:
            removes = request.POST.getlist('removes[]')
        table = get_object_or_404(Table, pk=pk)
        if adds is not None:
            for user_id in adds:
                person = get_object_or_404(Person, user_id=user_id)
                table.people.add(person)
        if removes is not None:
            for user_id in removes:
                person = get_object_or_404(Person, user_id=user_id)
                table.people.remove(person)
        table.save()
        return table_detail(request, pk=pk)
    else:
        from django.core import serializers
        table = Table.objects.get(pk=pk)
        members = table.people.all()
        followees = Followees.objects.get(user=request.user).people.all()
        others = followees.exclude(pk__in=members)
        members = serializers.serialize('json', members)
        others = serializers.serialize('json', others)
        return render(request, 'table_edit.html', {'table': table, 'members': members, 'others': others})

@login_required(login_url='/login/')
def table_delete(request, pk):
    table = get_object_or_404(Table, pk=pk)
    table.delete()
    return redirect('app.views.user_home')

@login_required(login_url='/login/')
def user_recent(request, pk):
    person = get_object_or_404(Person, pk=pk)
    return render(request, 'user_recent.html', {'person': person})

# from time import gmtime, strftime

# strftime("%a, %d %b %Y %I:%M %p", gmtime())
# 'Thu, 28 Jun 2001 12:17 PM'

###########################################################
############# Authentication and Registration #############
###########################################################

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = request.POST['username']
            password = request.POST['password1']
            user = authenticate(username=username, password=password)
            auth_login(request, user)
            return redirect(reverse('app.views.auth_info'))
    else:
        form = UserCreationForm()
    return render(request, "registration/register.html", {'form': form})

@never_cache
def login(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            return redirect(reverse('app.views.landing'))
    else:
        form = AuthenticationForm(request)
    return render(request, "registration/login.html", {'form': form})

def logout(request):
    if request.session.get('updated', False):
        del request.session['updated']
    auth_logout(request)
    request.session.flush()
    return redirect(reverse('app.views.landing'))

###########################################################
#################### New Account Setup ####################
###########################################################

@login_required(login_url='/login/')
def auth_info(request):
    return render(request, 'auth/info.html')

@login_required(login_url='/login/')
def auth_error(request, error):
    if error is not None:
        return render(request, 'auth/error.html', {'error': error})
    raise Exception('parameter missing for argument: error')

@login_required(login_url='/login/')
def auth_request(request):
    # in httplib's __init__.py, had to change
    #     check_hostname=True
    # to
    #     check_hostname= disable_ssl_certificate_validation ^ True
    scope = ["likes", "comments"]
    redirect_uri = api.get_authorize_login_url(scope=scope)
    return redirect(redirect_uri)
    # return render(request, 'auth/request.html')

@login_required(login_url='/login/')
def auth_process(request):
    error = request.GET.get('error')
    if error:
        reason = request.GET.get('error_reason')
        desc = request.GET.get('error_description')
        context = {
            'message': 'There was an error during authorization.',
            'error': error,
            'reason': reason,
            'desc': desc
        }
        return redirect('app.views.auth_error', error=context)
    else:
        code = request.GET.get('code')
        response = api.exchange_code_for_access_token(code)

        value = response[0]
        try:
            access_token = AccessToken.objects.get(user=request.user)
            access_token.value = value
            access_token.save(update_fields=['value'])
        except AccessToken.DoesNotExist:
            access_token = AccessToken.objects.create(user=request.user, value=value)

        user_info = response[1]
        user_id = user_info['id']
        username = user_info['username']
        full_name = user_info['full_name'].strip()
        profile_picture_url = user_info['profile_picture']
        # website=user_info['website']
        # bio=user_info['bio']

        person = Person.get_or_create_person(user_id, username, full_name, profile_picture_url)
        person.profile = request.user.get_username()
        person.save()

        return redirect(reverse('app.views.landing'))

###########################################################
######################## API Views ########################
###########################################################

@login_required(login_url='/login/')
@api_view(['GET', 'POST'])
def api_table_list(request, format=None):
    if request.method == 'GET':
        tables = Table.objects.filter(user=request.user).order_by('name')
        serializer = TableSerializer(tables, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        data = request.data
        serializer = TableSerializer(data=data)
        if serializer.is_valid():
            try:
                serializer.save(user=request.user)
            except IntegrityError:
                errors = {
                    "Unique field requirement violated: (user, name)"
                }
                return Response(errors, status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response(status=status.HTTP_400_BAD_REQUEST)

@login_required(login_url='/login/')
@api_view(['GET', 'POST', 'DELETE'])
def api_table_detail(request, pk, format=None):
    # passing a queryset to get_or_404 ensures only the authenicated user's
    # data is accessible through the API
    tables = Table.objects.filter(user=request.user)
    table = get_object_or_404(tables, pk=pk)
    if request.method == 'GET':
        serializer = TableSerializer(table)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = TableSerializer(table, data=data)
        if serializer.is_valid():
            try:
                serializer.save(user=request.user)
            except IntegrityError:
                errors = {
                    "Unique field requirement violated: (user, name)"
                }
                return Response(errors, status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        table.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    return Response(status=status.HTTP_400_BAD_REQUEST)

@login_required(login_url='/login/')
@api_view(['GET'])
def api_followees_list(request, format=None):
    if request.method == 'GET':
        followees = Followees.objects.filter(user=request.user)
        serializer = FolloweesSerializer(followees, many=True)
        return Response(serializer.data)
    return Response(status=status.HTTP_400_BAD_REQUEST)

def test_lb_(request):
    return render(request, 'test.html')
