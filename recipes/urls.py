from django.urls import path
from . import views

urlpatterns = [
    path('', views.recipe_scheduler, name='recipe_scheduler'),
]
