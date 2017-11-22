from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect, HttpResponse
from .models import WpUsers


def check_login(function):
    def wrap(request, *args, **kwargs):
        if request.COOKIES.get('user_email', False):
            user_email = request.COOKIES['user_email']
            user = WpUsers.objects.get(user_email = user_email)
            request.user = user
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied #return HttpResponseRedirect('http://www.yahoo.com')
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap