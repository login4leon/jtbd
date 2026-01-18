from django.http import HttpResponse
from django.shortcuts import render, redirect

from app01 import models
from app01.utils.forms import AgentAddForm, AgentEditForm


def agent_list(request):
    queryset = models.Agents.objects.all()
    return render(request, 'agent_list.html', {'queryset': queryset})


def agent_add(request):
    title = '新建Agent'
    if request.method == "GET":
        form = AgentAddForm()
        return render(request, 'agent_change.html', {'form': form, 'title': title})

    form = AgentAddForm(request.POST)
    if form.is_valid():
        form.save()
        return redirect('/agent/list/')
    return render(request, 'agent_change.html', {'form': form, 'title': title})

def agent_edit(request, nid):
    row_object = models.Agents.objects.filter(id=nid).first()

    if not row_object:
        return redirect('/agent/list/')

    title = '编辑Agent'

    if request.method == "GET":
        form = AgentEditForm(instance=row_object)
        return render(request, 'agent_change.html', {'form': form, 'title': title})

    form = AgentEditForm(request.POST, instance=row_object)
    if form.is_valid():
        form.save()
        return redirect('/agent/list/')
    return render(request, 'agent_change.html', {'form': form, 'title': title})

def agent_delete(request, nid):
    models.Agents.objects.filter(id=nid).delete()
    return redirect('/agent/list/')