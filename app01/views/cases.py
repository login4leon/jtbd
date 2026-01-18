import json

from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from app01 import models
from app01.utils.forms import FlowAddForm, StepAddForm, StepEditForm


def case_list(request):
    queryset = models.Cases.objects.all().order_by('-id')
    return render(request, 'case_list.html', {'queryset': queryset})

def case_detail(request, cid):
    # cid = request.GET.get('cid')
    case_data = models.Cases.objects.filter(id=cid).first()

    flow_data_list = []
    flow_index_list = models.Flows.objects.order_by('index').values_list('index', flat=True).distinct()
    for flow_index in flow_index_list:
        flows = models.Flows.objects.filter(index=flow_index).order_by('index')
        for flow in flows:
            row_object = models.Contexts.objects.filter(flow_id=flow.id, case_id=cid).first()
            context = json.loads(row_object.content)
            context = json.dumps(context, ensure_ascii=False, indent=2)
            steps = models.Steps.objects.filter(flow_id=flow.id).order_by('index')
            for step in steps:
                timer = models.StepTimer.objects.filter(case_id=cid, step_id=step.id).first()
                if timer:
                    step.start_time = timer.start_time
                    step.end_time = timer.end_time
                    step.delta = timer.delta
            flow_data = {
                'name': flow.name,
                'steps': steps,
                'context': context,
            }
            flow_data_list.append(flow_data)


    return render(request, 'case_detail.html', {'case_data': case_data, 'flow_data_list': flow_data_list})
