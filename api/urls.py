from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CompanyViewSet, JoinTheCompany, LeftTheCompany,
                    NewsViewSet, UserViewSet)

app_name = 'api'

router = DefaultRouter()
router.register(r'companies', CompanyViewSet, basename='api_companies')
router.register(r'companies/(?P<company_id>\d+)/news',
                NewsViewSet, basename='api_news')
router.register(r'companies/(?P<company_id>\d+)/users',
                UserViewSet, basename='api_users')

urlpatterns = [
    path('v1/companies/<int:company_id>/join/',
         JoinTheCompany.as_view(), name='api_join'),
    path('v1/companies/<int:company_id>/left/',
         LeftTheCompany.as_view(), name='api_left'),
    path('v1/', include(router.urls)),
]
