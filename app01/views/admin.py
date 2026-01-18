from django.http import HttpResponse
from django.shortcuts import render, redirect

from app01.utils.forms import LoginForm
from app01 import models
from app01.utils.captcha import generate_captcha

def captcha_image(request):
    image_bytes, code = generate_captcha()
    request.session['captcha'] = code.upper()
    request.session.set_expiry(60)
    return HttpResponse(image_bytes, content_type='image/png')
def login(request):
    if request.method == 'GET':
        form = LoginForm()
        return render(request, 'admin_login.html', {'form': form})

    form = LoginForm(request.POST)
    if form.is_valid():
        # 下面语句使用pop把captcha从cleaned_data中删除，以便剩下的cleaned_data用于数据库查询
        if form.cleaned_data.pop('captcha').upper() != request.session.get('captcha').upper():
            form.add_error('captcha', '验证码错误')
            return render(request, 'admin_login.html', {'form': form})

        # 去掉captcha的cleaned_data可以直接用于数据库查询
        admin_object = models.Admin.objects.filter(**form.cleaned_data).first()
        if not admin_object:
            form.add_error('password', '用户名或密码错误')
            return render(request, 'admin_login.html', {'form': form})

        # 密码正确，设置cookie
        request.session['info'] = { 'role': 'admin', 'id': admin_object.id, 'username': admin_object.username }
        request.session.set_expiry(60*60*24)
        return redirect('/agent/list/')
    return render(request, 'admin_login.html', {'form': form})

def logout(request):
    print('admin')
    request.session.clear()
    return redirect('/admin/login/')

