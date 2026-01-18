from django.http import StreamingHttpResponse, JsonResponse
import redis, json, time
from django.shortcuts import render

from app01.tasks import stream_think


def sse_stream(request):
    case_id = request.GET.get('case_id')
    def event_stream():
        r_sse = redis.Redis(host='localhost', port=6379, db=3)
        while True:
            time.sleep(2)
            msg = r_sse.brpop(case_id, timeout=5)  # 阻塞弹出
            if not msg:  # 超时
                # yield 'data: {}\n\n'
                continue
            chunk = msg[1].decode()
            if chunk == '[DONE]':
                yield 'data: [DONE]\n\n'
                break
            yield f'data: {json.dumps({"text": chunk})}\n\n'

    return StreamingHttpResponse(event_stream(), content_type='text/event-stream')


def start_task(request):
    sentences = [
        "我正在理解你的问题...",
        "让我检索相关知识...",
        "开始生成回答...",
        "3 + 5 = 8",
        "完成！"
    ]
    r = redis.Redis(host='localhost', port=6379, db=2)
    for s in sentences:
        time.sleep(1)  # 模拟思考
        r.lpush('case_id', s)  # 推入队列
    r.lpush('case_id', '[DONE]')  # 结束标记

    return render(request, 'sse.html')

def sse_test(request):

    def event_stream():
        r = redis.Redis(host='localhost', port=6379, db=2)
        while True:
            time.sleep(6)
            msg = r.brpop('case_id', timeout=5)  # 阻塞弹出
            if not msg:  # 超时
                # yield 'data: {}\n\n'
                continue
            chunk = msg[1].decode()
            if chunk == '[DONE]':
                yield 'data: [DONE]\n\n'
                break
            yield f'data: {json.dumps({"text": chunk})}\n\n'

    return StreamingHttpResponse(event_stream(), content_type='text/event-stream')