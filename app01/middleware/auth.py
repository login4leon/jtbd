from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect

class AuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # 无需身份验证的链接
        white_list = [
            '/admin/login/',
            '/captcha/',
            '/login/',
            '/register/',
            '/admin/logout/',
            '/logout/'
        ]
        # 非管理员用户可以访问的链接
        user_list = [
            '/',
            '/jtbd/opencase/',
            '/jtbd/listcase/',
            '/jtbd/pincase/',
            '/jtbd/delcase/',
            '/jtbd/work/',
            '/jtbd/output/',
            '/sse/stream/'
        ]

        if request.path_info in white_list:
            return

        info_dict = request.session.get('info')
        if not info_dict:
            return redirect('/login/')

        if info_dict['role'] == 'admin':
            return
        else:
            if request.path_info in user_list:
                return
            else:
                return redirect('/admin/login/')

        # return redirect('/login/')