from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from .models import WpUsers
from catalogue_service.settings_local import AUTH_LOGIN_URL, AUTH_EMAIL_KEY, AUTH_REDIRECT_COOKIE, AUTH_SESSION_COOKIE_DOMAIN
from stylist_management.models import StylistProfile

# https://docs.djangoproject.com/en/1.11/topics/http/decorators/
# https://simpleisbetterthancomplex.com/2015/12/07/working-with-django-view-decorators.html
def check_login(function):
    def wrap(request, *args, **kwargs):
        if request.COOKIES.get(AUTH_EMAIL_KEY, False):
            user_email = request.COOKIES[AUTH_EMAIL_KEY]

            try:
                user = WpUsers.objects.get(user_email = user_email)
                # check if the user is active
                if user.is_active:
                    request.user = user
                    return function(request, *args, **kwargs)
            except WpUsers.DoesNotExist:
                context = {'user_email': user_email}
                return render(request, 'shopping_tool/no_user.html', context) 

        response_redirect = HttpResponseRedirect(AUTH_LOGIN_URL)
        response_redirect.set_cookie(AUTH_REDIRECT_COOKIE, request.build_absolute_uri(), domain=AUTH_SESSION_COOKIE_DOMAIN)
        return response_redirect
        #raise PermissionDenied #return HttpResponseRedirect('http://www.yahoo.com')
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap