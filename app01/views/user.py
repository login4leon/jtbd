from django.http import HttpResponse
from django.shortcuts import render, redirect

from app01.utils.forms import RegisterForm, LoginForm
from app01 import models
from app01.utils.encrypt import md5

def register(request):
    if request.method == 'GET':
        form = RegisterForm()
        return render(request, 'register.html', {'form': form})

    form = RegisterForm(request.POST)
    if form.is_valid():
        # 下面语句使用pop把captcha从cleaned_data中删除，以便剩下的cleaned_data用于数据库查询
        if form.cleaned_data.pop('captcha').upper() != request.session.get('captcha').upper():
            form.add_error('captcha', '验证码错误')
            return render(request, 'register.html', {'form': form})

        # 去掉captcha的cleaned_data可以直接用于数据库查询
        user_exists = models.Users.objects.filter(username=form.cleaned_data.get('username')).first()
        if user_exists:
            form.add_error('username', '用户名被占用')
            return render(request, 'register.html', {'form': form})
        # 保存记录
        user = form.save(commit=False)
        user.password = md5(form.cleaned_data.get('password'))
        user.save()
        # 设置cookie
        request.session['info'] = { 'role': 'user', 'id': user.id, 'username': user.username }
        request.session.set_expiry(60*60*24*365)
        return redirect('/')
    return render(request, 'register.html', {'form': form})

def login(request):
    if request.method == 'GET':
        form = LoginForm()
        return render(request, 'login.html', {'form': form})

    form = LoginForm(request.POST)
    if form.is_valid():
        # 下面语句使用pop把captcha从cleaned_data中删除，以便剩下的cleaned_data用于数据库查询
        if form.cleaned_data.pop('captcha').upper() != request.session.get('captcha').upper():
            form.add_error('captcha', '验证码错误')
            return render(request, 'login.html', {'form': form})

        # 去掉captcha的cleaned_data可以直接用于数据库查询
        user_object = models.Users.objects.filter(**form.cleaned_data).first()
        if not user_object:
            form.add_error('password', '用户名或密码错误')
            return render(request, 'login.html', {'form': form})

        # 密码正确，设置cookie
        request.session['info'] = { 'role': 'user', 'id': user_object.id, 'username': user_object.username }
        request.session.set_expiry(60*60*24*365)
        return redirect('/')
    return render(request, 'login.html', {'form': form})

def logout(request):
    print('user')
    request.session.clear()
    return redirect('/login/')

