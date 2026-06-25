from django.urls import path
#from .views import HomePageView
from .views import views, datasets, filtering_terms, synonyms, descendants, permits, budget, rounding_counts, connections, service_status, identity_provider, verifier, admin_settings
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
    path('connections', connections.default_view, name='connections'),
    path('service_status', service_status.default_view, name='service_status'),
    path('identity_provider', identity_provider.default_view, name='identity_provider'),
    path('verifier', verifier.default_view, name='verifier'),
    path('admin_settings', admin_settings.default_view, name='admin_settings')
]