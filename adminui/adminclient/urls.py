from django.urls import path
#from .views import HomePageView
from .views import views, datasets
app_name = 'adminclients'

urlpatterns = [
    path('', views.default_view, name='index'),
    path('entry_types', views.entry_types, name='entry_types'),
    path('datasets', datasets.default_view, name='datasets')
]