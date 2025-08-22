from django.urls import path
#from .views import HomePageView
from .views import views, datasets, filtering_terms, synonyms, descendants, permits, budget, rounding_counts, connections
app_name = 'adminclients'

urlpatterns = [
    path('', views.default_view, name='index'),
    path('entry_types', views.entry_types, name='entry_types'),
    path('datasets', datasets.default_view, name='datasets'),
    path('filtering_terms', filtering_terms.default_view, name='filtering_terms'),
    path('synonyms', synonyms.default_view, name='synonyms'),
    path('descendants', descendants.default_view, name='descendants'),
    path('permits', permits.default_view, name='permits'),
    path('budget', budget.default_view, name='budget'),
    path('rounding_counts', rounding_counts.default_view, name='rounding_counts'),
    path('connections', connections.default_view, name='connections')
]