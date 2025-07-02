from django.urls import path
#from .views import HomePageView
from . import views
app_name = 'adminclients'

urlpatterns = [
    path('', views.default_view, name='index'),
    path('entry_types', views.entry_types, name='entry_types')
]