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
    path('<int:id>/create_news/', views.create_news, name='create_news'),
    path('<int:id>/users/', views.staff_page, name='staff'),
    path(
        '<int:id>/users/<int:user_id>/set_moderator_role/',
        views.set_moderator_status, name='set_moderator'
    ),
    path(
        '<int:id>/users/<int:user_id>/set_user_role/',
        views.set_user_status, name='set_user'
    ),
]
