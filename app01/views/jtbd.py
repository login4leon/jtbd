import json
import threading

import redis
import re

from dateutil.relativedelta import relativedelta
from django.utils import timezone
from django.db.models import Avg, Q
from django.db.models.functions import TruncMonth
from django.http import JsonResponse
from django.shortcuts import render

from app01 import models
from app01.utils.llm import LLMUtil


def step_runner(case_id, step_id):
    # 先确认该步骤是否已经执行过（在已完成步骤队列中），如果在，则退出。
    r_step = redis.Redis(host='localhost', port=6379, db=1)
    exists = r_step.hexists(case_id, step_id)
    if exists:
        return
    # 步骤开始执行
    start_time = timezone.now()
    agent_id = models.Steps.objects.get(id=step_id).agent_id
    # 获取该步骤历史平均耗时int_time
    avg_delta = models.StepTimer.objects.filter(step_id=step_id).aggregate(Avg('delta'))['delta__avg']
    if avg_delta is not None:
        int_delta = round(avg_delta)
    else:
        int_delta = 0
    # 以指定角色召唤AI（bot）
    bot = LLMUtil(agent_id)
    # 向消息队列推送信息，记录bot开始工作
    r_sse = redis.Redis(host='localhost', port=6379, db=3)
    r_sse.lpush(case_id, bot.name + ': 开始工作（平均耗时' + str(int_delta) + '秒)...')  # 推入队列
    # 从context完善角色提示词
    r_context = redis.Redis(host='localhost', port=6379, db=2, decode_responses=True)
    dict_context = r_context.hgetall(case_id)
    # 提取提示词模板里的字段（如：{product)）
    keys = re.findall(r'\{(\w+)}', bot.user_prompt)
    sub = {k: dict_context.get(k, '') for k in keys}
    bot.user_prompt = bot.user_prompt.format(**sub)
    # 获得AI的输出bot_output
    bot_output = bot.chat()
    # 记录执行时间
    end_time = timezone.now()
    delta = end_time - start_time
    delta = delta.total_seconds()
    models.StepTimer.objects.create(case_id=case_id, step_id=step_id, start_time=start_time, end_time=end_time,
                                    delta=delta)
    # 把新的bot_output内容存入context（redis）
    key = models.Agents.objects.get(pk=agent_id).output
    content = (
            dict_context.get(key, '') + bot_output['content']  # 键在则累加新内容，键不在则新建
    )
    r_context.hset(case_id, key, content)

    # 设置函数，对较长的推送信息进行裁剪
    def truncate_text(text, max_length=40):
        if len(text) > max_length:
            return text[:max_length - 3] + '...'
        return text

    # 向消息队列推送信息，记录bot工作产出
    r_sse.lpush(case_id, bot.name + ': 工作结果 >>>   ' + truncate_text(bot_output['content']))  # 推入队列
    # 向消息队列推送信息，记录bot结束工作
    r_sse.lpush(case_id, bot.name + ': 结束工作！')  # 推入队列
    # 向已完成步骤队列推入本步骤的step_id
    r_step.hset(case_id, step_id, bot_output['content'])
    # 手动断开所有redis连接
    r_step.close()
    r_sse.close()
    r_context.close()


class Workflow:
    def __init__(self, case_id, *steps) -> None:
        self.steps = steps
        self.case_id = case_id

    def run(self):
        for step in self.steps:
            step_runner(self.case_id, step)


def flow_runner(flow_id, case_id):
    # 准备本flow的step列表
    steps = []
    raw_steps = models.Steps.objects.filter(flow_id=flow_id).order_by('index')
    for raw_step in raw_steps:
        steps.append(raw_step.id)
    # 执行flow
    wf = Workflow(case_id, *steps)
    wf.run()
    # 保存本flow的最终context
    r_context = redis.Redis(host='localhost', port=6379, db=2, decode_responses=True)
    dict_context = r_context.hgetall(case_id)
    str_context = json.dumps(dict_context)
    models.Contexts.objects.create(content=str_context, flow_id=flow_id, case_id=case_id)
    # 手动断开redis连接
    r_context.close()


def homepage(request):
    return render(request, 'index.html')


def opencase(request):
    # 接收外部数据，建立新case
    product = request.GET.get('product')
    info = request.GET.get('info')
    user_id = request.GET.get('user_id')
    start_time = timezone.now()
    case = models.Cases.objects.create(product=product, info=info, user_id=user_id, start_time=start_time)
    # 向队列中推入case
    # r_work = redis.Redis(host='localhost', port=6379, db=4)
    # r_work.lpush('work_queue', case.pk)

    return JsonResponse({'status': True, 'case': case.pk, 'start_time': case.start_time})


def listcase(request):
    cases = []
    user_id = request.GET.get('user_id')
    # 先整理置顶历史记录
    queryset = models.Cases.objects.exclude(start_time=None).filter(user_id=user_id, pinned=True).values_list('id', 'product',
                                                                                                 'info',
                                                                                                 'start_time',
                                                                                                 'closed',
                                                                                                 'pinned').order_by(
            '-pinned_time')
    if queryset.exists():
        pinned_cases = []
        for obj in queryset:
            case = {'id': obj[0],
                    'product': obj[1],
                    'info': obj[2],
                    'start_time': timezone.localtime(obj[3]).strftime('%Y-%m-%d %H:%M:%S'),
                    'closed': obj[4],
                    'pinned': obj[5]}
            pinned_cases.append(case)
        cases.append({
            'title': '置顶',
            'key': 'pinned',
            'list': pinned_cases
        })


    months = (models.Cases.objects.exclude(Q(start_time=None) | Q(pinned=True)).filter(user_id=user_id).annotate(month=TruncMonth('start_time')).values('month').distinct().order_by('month'))
    if months.exists():
        for m in months:
            start = m['month']
            end = (start + relativedelta(months=1))
            qs = models.Cases.objects.exclude(Q(start_time=None) | Q(pinned=True)).filter(user_id=user_id, start_time__gte=start, start_time__lt=end).values_list('id', 'product',
                                                                                                     'info',
                                                                                                     'start_time',
                                                                                                     'closed',
                                                                                                     'pinned').order_by(
            '-start_time')
            monthly_cases = []
            for obj in qs:
                case = {'id': obj[0],
                        'product': obj[1],
                        'info': obj[2],
                        'start_time': timezone.localtime(obj[3]).strftime('%Y-%m-%d %H:%M:%S'),
                        'closed': obj[4],
                        'pinned': obj[5]}
                monthly_cases.append(case)
            cases.append({
                'title': start.strftime('%Y年%m月'),
                'key': start.strftime('%Y-%m'),
                'list': monthly_cases
            })

    return JsonResponse({'status': True, 'cases': cases})

def pincase(request):
    case_id = request.GET.get('case_id')
    case = models.Cases.objects.filter(id=case_id).first()
    case.pinned = not case.pinned
    case.pinned_time = timezone.now()
    case.save()

    return JsonResponse({'status': True})

def delcase(request):
    case_id = request.GET.get('case_id')
    models.Cases.objects.filter(id=case_id).delete()
    return JsonResponse({'status': True})



def showideas(solutions):
    ideas = []
    solution_list = solutions.split('\n')
    for row in solution_list:
        if not re.match(r'^.+---.+---.+---.+$', row):
            continue
        idea = {}
        items = row.split('---')
        idea['opportunity'] = items[0].strip()
        idea['customer'] = items[1].strip()
        idea['design'] = items[2].strip()
        idea['slogan'] = items[3].strip()
        ideas.append(idea)
    return ideas


# views.py
def work(request):
    case_id = request.GET.get('case_id')
    # 仅push任务，不阻塞
    r_queue = redis.Redis(host='localhost', port=6379, db=4)
    r_queue.lpush('work_queue', case_id)
    # 手动断开redis连接
    r_queue.close()
    return JsonResponse({'status': True, 'msg': '任务已提交'})


def output(request):
    case = {}
    case_id = request.GET.get('case_id')
    r_context = redis.Redis(host='localhost', port=6379, db=2, decode_responses=True)

    case['product'] = r_context.hget(case_id, 'product')
    case['info'] = r_context.hget(case_id, 'info')
    ideas = showideas(r_context.hget(case_id, 'solution'))
    # 手动断开redis连接
    r_context.close()

    return JsonResponse({'status': True, 'case': case, 'ideas': ideas})

def result(request):
    case_id = request.GET.get('case_id')
    r_res = redis.Redis(host='localhost', port=6379, db=5, decode_responses=True)
    ideas = r_res.get(f'{case_id}:ideas')
    print(ideas)
    # 手动断开redis连接
    r_res.close()
    if ideas:
        return JsonResponse({'status': True, 'ideas': json.loads(ideas)})
    return JsonResponse({'status': False})
