from django.conf.urls import url
#from django.urls import path
from django.urls import path
from django.contrib import admin,admindocs
from .views import index, userdetails, delete_integration, view_integration
admin.autodiscover()
app_name = 'web'

urlpatterns = [


    path("user/", userdetails, name="home"),
    path("user/<int:id>", delete_integration, name="home"),
    path("accounts/<int:id>/", view_integration, name="home"),
    url(r"^(?P<path>.*)$", index, name="home"),
]
