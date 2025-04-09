import socket
from django.http import HttpResponse

class BrokenPipeErrorMiddleware:
    """
    中间件用于捕获并优雅地处理Broken Pipe错误
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        # 检查各种类型的连接断开错误
        if isinstance(exception, (socket.error, BrokenPipeError)) or \
           'Broken pipe' in str(exception) or \
           'Connection reset by peer' in str(exception):
            # 记录最小错误日志而不是完整堆栈跟踪
            print(f"客户端连接断开: {str(exception)[:100]}")
            return HttpResponse("连接断开", status=499)  # 使用499状态码（客户端关闭请求）
        return None
