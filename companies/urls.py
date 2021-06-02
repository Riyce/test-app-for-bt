from django.urls import path

from . import views

urlpatterns = [
    path('create/', views.create_an_organization, name='create'),
    path('', views.index, name='index'),
    path('<int:id>/', views.company, name='company'),
    path('<int:id>/left/', views.left_an_organization, name='left'),
    path('<int:id>/join/', views.join_an_organization, name='join'),
    path('<int:id>/delete/', views.delete_an_organization, name='delete'),
    path('<int:id>/update/', views.update_an_organization, name='update'),
]
