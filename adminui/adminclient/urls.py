from django.urls import path
#from .views import HomePageView
from .views import views, datasets, filtering_terms, synonyms
app_name = 'adminclients'

urlpatterns = [
    path('', views.default_view, name='index'),
    path('entry_types', views.entry_types, name='entry_types'),
    path('datasets', datasets.default_view, name='datasets'),
    path('filtering_terms', filtering_terms.default_view, name='filtering_terms'),
    path('synonyms', synonyms.default_view, name='synonyms')
]