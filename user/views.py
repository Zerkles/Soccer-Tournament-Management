from datetime import datetime

from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotAllowed
from django.utils import timezone

from .models import User


def login(request):
    if request.method == 'GET':
        template = loader.get_template('userLogin.html')
        return HttpResponse(template.render({'auth_user': request.session.get('auth_user', None)}, request))

    elif request.method == 'POST':
        data = request.POST
        user = User.objects.filter(name=data['name'], password=data['password']).values()

        if not user:
            return HttpResponse("Unauthorized", status=401)

        user = user[0]
        user.pop('birthday')
        request.session['auth_user'] = user
        return HttpResponseRedirect("/tournament/")

    else:
        return HttpResponseNotAllowed(permitted_methods=['GET', 'POST'])


def logout(request):
    if request.method == 'GET':
        request.session['auth_user'] = None
        return HttpResponseRedirect('/tournament/')
    else:
        return HttpResponseNotAllowed(permitted_methods=['GET'])


def register(request):
    if request.method == 'GET':
        template = loader.get_template('userRegister.html')
        return HttpResponse(template.render({'auth_user': request.session.get('auth_user', None)}, request))
    else:
        return HttpResponseNotAllowed(permitted_methods=['GET'])


def user(request):
    if request.method == 'GET':
        if not authorized(session=request.session):
            return HttpResponse('Unauthorized', status=401)

        all_users = User.objects.all().values()
        context = {'all_users': all_users, 'auth_user': request.session.get('auth_user', None)}

        template = loader.get_template('userViewAll.html')
        return HttpResponse(template.render(context, request))

    elif request.method == 'POST':
        data = request.POST

        if datetime.strptime(data['birthday'], '%Y-%m-%d') > timezone.now().replace(tzinfo=None):
            return HttpResponse("Bad request - user cannot be born in future.", status=400)

        new_user = User(name=data['name'], password=data['password'], email=data['email'], birthday=data['birthday'])
        new_user.save()
        return HttpResponseRedirect('/user/login/')

    else:
        return HttpResponseNotAllowed(permitted_methods=['GET', 'POST'])


def user_arg(request, id):
    if not authorized(session=request.session, permitted_user_id=id):
        return HttpResponse('Unauthorized', status=401)

    user = User.objects.get(id=id)

    if request.method == 'GET':
        template = loader.get_template('userView.html')
        context = {'user': user, 'auth_user': request.session.get('auth_user', None)}
        return HttpResponse(template.render(context, request))

    elif request.method == 'POST':
        data = request.POST

        user.name = data['name']
        user.password = data['password']
        user.email = data['email']
        user.birthday = data['birthday']

        if authorized(session=request.session):
            user.usergroup = data['usergroup']

        user.save()

        if user.id == request.session.get('auth_user', None)['id']:
            user_dict = User.objects.filter(id=user.id).values()[0]
            user_dict.pop('birthday')
            request.session['auth_user'] = user_dict

        return HttpResponseRedirect(f'/user/{user.id}/')

    elif request.method == 'DELETE':
        user.delete()
        return HttpResponseRedirect(f'/user/')

    else:
        return HttpResponseNotAllowed(permitted_methods=['GET', 'POST', 'DELETE'])


def user_delete(request, id):
    request.method = 'DELETE'
    return user_arg(request, id)


def authorized(session, permitted_user_id=-1):
    if session.get('auth_user', None) is not None:
        user_requesting = session['auth_user']['id']
    else:
        user_requesting = 0

    authorized_users = [x.id for x in User.objects.filter(usergroup='admin')] + [permitted_user_id]

    if user_requesting in authorized_users:
        return True

    return False
