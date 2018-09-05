from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect, HttpResponse
from .models import WpUsers
from catalogue_service.settings_local import AUTH_LOGIN_URL, AUTH_EMAIL_KEY, AUTH_REDIRECT_COOKIE, AUTH_SESSION_COOKIE_DOMAIN

# https://docs.djangoproject.com/en/1.11/topics/http/decorators/
# https://simpleisbetterthancomplex.com/2015/12/07/working-with-django-view-decorators.html
def check_login(function):
    def wrap(request, *args, **kwargs):
        if True:
            user_email = 'pamela@allume.co' #request.COOKIES[AUTH_EMAIL_KEY]
            user = WpUsers.objects.get(user_email = user_email)
            request.user = user
            return function(request, *args, **kwargs)
        else:
            response_redirect = HttpResponseRedirect(AUTH_LOGIN_URL)
            response_redirect.set_cookie(AUTH_REDIRECT_COOKIE, request.build_absolute_uri(), domain=AUTH_SESSION_COOKIE_DOMAIN)
            return response_redirect
            #raise PermissionDenied #return HttpResponseRedirect('http://www.yahoo.com')
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap