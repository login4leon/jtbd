#!/envs/jtbd/bin/python
import os, sys, django, redis, json, logging, threading
from datetime import timezone

# 1. 把 Django 加载进来（独立脚本必须）
sys.path.insert(0, '/srv/django-app/jtbd')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'JTBDonDjango.settings')
django.setup()

# 2. 引入你自己的模型与函数
from app01.models import Cases, Flows, Contexts
from app01.views.jtbd import showideas, flow_runner   # 你原来的转换函数

# 3. 日志打到文件，方便 systemd 查看
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[logging.FileHandler('/srv/django-app/logs/worker.log')]
)

# 4. 连接 Redis（与 Web 层同一实例）
r_queue = redis.Redis(host='localhost', port=6379, db=4, decode_responses=True)   # 任务队列
r_res   = redis.Redis(host='localhost', port=6379, db=5, decode_responses=True)   # 结果缓存

# 5. 真正的长任务（原来写在 views.py 里的逻辑搬过来）
def do_long_work(case_id: str):
    logging.info(f'start work case={case_id}')
    case = Cases.objects.get(pk=case_id)

    # ===== 以下是你原来 /jtbd/work/ 里的全部代码 =====
    r_context = redis.Redis(host='localhost', port=6379, db=2, decode_responses=True)
    exists = r_context.hexists(case_id, 'product')
    if not exists: #新case，从头开始
        product = case.product
        info = case.info
        # 把初始信息插入Contexts表单和redis，root子流程的结果
        dict_context = {'product': product, 'info': info}
        root = Flows.objects.filter(index=0).first()
        Contexts.objects.create(
            content=json.dumps(dict_context),
            flow_id=root.id,
            case_id=case.pk
        )
        r_context.hset(case_id, mapping=dict_context)

    # 循环遍历所有工作子流程（root子流程除外）
    flow_index_list = Flows.objects.exclude(index=0).order_by('index').values_list('index', flat=True).distinct()
    for flow_index in flow_index_list:
        flows = Flows.objects.filter(index=flow_index).order_by('index')
        if len(flows) == 1:
            flow_runner(flows[0].id, case_id)
        else:
            threads = [threading.Thread(target=flow_runner, args=(flow.id, case_id)) for flow in flows]
            # 启动所有线程
            for t in threads: t.start()
            # 等待所有线程完成
            for t in threads: t.join()

    # 推 SSE 结束标记
    r_sse = redis.Redis(host='localhost', port=6379, db=3)
    r_sse.lpush(case_id, '[DONE]')

    # 写回结果到redis
    ideas = showideas(r_context.hget(case_id, 'solution'))
    r_res.set(f'{case_id}:ideas', json.dumps(ideas), ex=3600)

    # 清空redis中的context和已完成step队列
    # r_context.delete(case_id)
    # r_step = redis.Redis(host='localhost', port=6379, db=1)
    # r_step.delete(case_id)

    # 把执行时间计入数据库Cases表
    case.end_time = timezone.now()
    case.delta = (case.end_time - case.start_time).total_seconds()
    case.closed = True
    case.save()

    logging.info(f'finish work case={case_id} delta={case.delta}s')

# 6. 阻塞式消费者（永不退出）
def consume():
    logging.info('worker started, waiting for tasks...')
    while True:
        _, case_id = r_queue.brpop('work_queue', timeout=30)   # 30s 心跳保活
        if case_id:
            try:
                do_long_work(case_id)
            except Exception as e:
                logging.exception(f'case {case_id} failed: {e}')

if __name__ == '__main__':
    consume()