from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView)

from .views import CompanyViewSet, NewsViewSet, UserViewSet, LeftTheCompany, JoinTheCompany

router = DefaultRouter()
router.register('companies', CompanyViewSet)
router.register('companies/(?P<company_id>\d+)/news',
                NewsViewSet, basename='news')
router.register('companies/(?P<company_id>\d+)/users',
                UserViewSet, basename='users')

urlpatterns = [
    path('v1/companies/<int:company_id>/join/', JoinTheCompany.as_view()),
    path('v1/companies/<int:company_id>/left/', LeftTheCompany.as_view()),
    path('v1/', include(router.urls)),
    path(
        'v1/token/',
        TokenObtainPairView.as_view(),
        name='token_obtain_pair'
    ),
    path(
        'v1/token/refresh/',
        TokenRefreshView.as_view(),
        name='token_refresh'
    ),
]