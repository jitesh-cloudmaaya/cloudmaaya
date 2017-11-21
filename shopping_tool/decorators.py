from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect, HttpResponse


def check_login(function):
    def wrap(request, *args, **kwargs):
        if request.COOKIES.get('username', False):
            user = request.COOKIES['username']
            request.user = user
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied #return HttpResponseRedirect('http://www.yahoo.com')
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap