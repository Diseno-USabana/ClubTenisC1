# informes/urls.py
from django.urls import path
from .views import informes_view

urlpatterns = [
    path('', informes_view, name="informes"),  # /informes/
]
