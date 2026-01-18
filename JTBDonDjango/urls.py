"""
URL configuration for JTBDonDjango project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# from django.contrib import admin
from django.urls import path
from app01.views import admin, agents, flows, jtbd, cases, sse, user

urlpatterns = [
    #    path('admin/', admin.site.urls),
    path('login/', user.login, name='login'),
    path('sse/start/', sse.start_task, name='start_task'),
    path('sse/stream/', sse.sse_stream, name='sse_stream'),
    path('sse/test/', sse.sse_test),
    path('', jtbd.homepage),
    path('jtbd/opencase/', jtbd.opencase, name='opencase'),
    path('jtbd/work/', jtbd.work),
    path('jtbd/output/', jtbd.output),
    path('jtbd/listcase/', jtbd.listcase, name='listcase'),
    path('jtbd/pincase/', jtbd.pincase, name='pincase'),
    path('jtbd/delcase/', jtbd.delcase, name='delcase'),

    # 运行监控
    path('case/list/', cases.case_list),
    path('case/<int:cid>/detail/', cases.case_detail),
    # Agent管理
    path('agent/list/', agents.agent_list),
    path('agent/add/', agents.agent_add),
    path('agent/<int:nid>/edit/', agents.agent_edit),
    path('agent/<int:nid>/delete/', agents.agent_delete),

    # Flow管理
    path('flow/list/', flows.flow_list),
    path('flow/add/', flows.flow_add),
    path('flow/delete/', flows.flow_delete),
    path('flow/edit/', flows.flow_edit),
    path('flow/detail/', flows.flow_detail),
    path('step/<int:fid>/list/', flows.step_list),
    path('step/add/', flows.step_add),
    path('step/edit/', flows.step_edit),
    path('step/delete/', flows.step_delete),
    path('step/detail/', flows.step_detail),

    # 登录管理
    path('admin/login/', admin.login),
    path('admin/logout/', admin.logout),
    path('captcha/', admin.captcha_image, name='captcha'),

    path('login/', user.login),
    path('logout/', user.logout),
    path('register/', user.register),

]
