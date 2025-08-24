from django.urls import path
from . import views

urlpatterns = [
    path('', views.random_quote, name='random_quote'),
    path('submit/', views.submit_quote, name='submit_quote'),
    path('popular/', views.popular, name='popular'),
    path('vote/<int:quote_id>/<str:action>/', views.vote, name='vote'),
    path('popular/views/', views.popular_by_views, name='popular_by_views'),
    path('popular/dislikes/', views.popular_by_dislikes, name='popular_by_dislikes'),
    path('dashboard/', views.dashboard, name='dashboard'),
]
