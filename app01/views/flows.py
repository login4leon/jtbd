from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from app01 import models
from app01.utils.forms import FlowAddForm, StepAddForm, StepEditForm


def flow_list(request):
    queryset = models.Flows.objects.all().order_by('index')
    form = FlowAddForm()
    context = {
        'queryset': queryset,  # 给子流程列表传数据
        'form': form,  # 给新建子流程模态框（弹出）传递form
    }
    return render(request, 'flow_list.html', context)


@csrf_exempt
def flow_add(request):
    form = FlowAddForm(request.POST)
    if form.is_valid():
        form.save()
        return JsonResponse({'status': True})
    return JsonResponse({'status': False, 'errors': form.errors})


def flow_delete(request):
    fid = request.GET.get('fid')
    exists = models.Flows.objects.filter(id=fid).exists()
    if not exists:
        return JsonResponse({'status': False, 'errors': '数据不存在'})
    models.Flows.objects.filter(id=fid).delete()
    return JsonResponse({'status': True})


@csrf_exempt
def flow_edit(request):
    fid = request.GET.get('fid')
    row_object = models.Flows.objects.filter(id=fid).first()

    if not row_object:
        return JsonResponse({'status': False, 'errors': '数据不存在'})

    form = FlowAddForm(request.POST, instance=row_object)
    if form.is_valid():
        form.save()
        return JsonResponse({'status': True})
    return JsonResponse({'status': False, 'errors': form.errors})


def flow_detail(request):
    fid = request.GET.get('fid')
    row_dict = models.Flows.objects.filter(id=fid).values('name', 'index', 'description', 'parent').first()

    if not row_dict:
        return JsonResponse({'status': False, 'errors': '数据不存在'})
    result = {
        'status': True,
        'data': row_dict,
    }
    return JsonResponse(result)


def step_list(request, fid):
    # fid = request.GET.get('fid')
    request.session['fid'] = fid
    queryset = models.Steps.objects.filter(flow_id=fid).order_by('index')
    row_object = models.Flows.objects.filter(id=fid).first()
    if not row_object:
        return redirect('/flow/list')
    form = StepAddForm()
    context = {
        'queryset': queryset,
        'row_object': row_object,
        'form': form,
    }
    return render(request, 'step_list.html', context)

@csrf_exempt
def step_add(request):
    form = StepAddForm(request.POST)
    form.instance.flow_id = request.session['fid']
    if form.is_valid():
        form.save()
        return JsonResponse({'status': True})
    return JsonResponse({'status': False, 'errors': form.errors})

@csrf_exempt
def step_edit(request):
    sid = request.GET.get('sid')
    row_object = models.Steps.objects.filter(id=sid).first()

    if not row_object:
        return JsonResponse({'status': False, 'errors': '数据不存在'})

    form = StepEditForm(request.POST, instance=row_object)
    form.instance.flow_id = request.session['fid']
    if form.is_valid():
        form.save()
        return JsonResponse({'status': True})
    return JsonResponse({'status': False, 'errors': form.errors})


def step_delete(request):
    sid = request.GET.get('sid')
    exists = models.Steps.objects.filter(id=sid).exists()
    if not exists:
        return JsonResponse({'status': False, 'errors': '数据不存在'})
    models.Steps.objects.filter(id=sid).delete()
    return JsonResponse({'status': True})


def step_detail(request):
    sid = request.GET.get('sid')
    row_dict = models.Steps.objects.filter(id=sid).values('index', 'agent').first()

    if not row_dict:
        return JsonResponse({'status': False, 'errors': '数据不存在'})
    result = {
        'status': True,
        'data': row_dict,
    }
    return JsonResponse(result)
