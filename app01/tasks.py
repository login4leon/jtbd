import time, json, redis
from celery import shared_task

@shared_task(bind=True)
def stream_think(self, question):
    sentences = [
        "我正在理解你的问题...",
        "让我检索相关知识...",
        "开始生成回答...",
        "3 + 5 = 8",
        "完成！"
    ]
    r = redis.Redis(host='localhost', port=6379, db=1)
    for s in sentences:
        time.sleep(1)        # 模拟思考
        r.lpush('case_id', s)         # 推入队列
    r.lpush('case_id', '[DONE]')      # 结束标记