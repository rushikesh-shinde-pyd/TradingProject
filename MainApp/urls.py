from django.urls import path
from .views import *

app_name = 'mainapp'

urlpatterns = [
    path('upload/', upload_csv, name='upload_csv'),
    path('', index, name='index'),
]