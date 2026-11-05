from django.urls import path
from . import views

urlpatterns = [
    path('', views.drug_list, name='drug_list'),
    path('search/', views.drug_search, name='drug_search'),
]