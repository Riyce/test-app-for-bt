from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView)

from .views import (CompanyViewSet, JoinTheCompany, LeftTheCompany,
                    NewsViewSet, UserViewSet)

router = DefaultRouter()
router.register(r'companies', CompanyViewSet)
router.register(r'companies/(?P<company_id>\d+)/news',
                NewsViewSet, basename='news')
router.register(r'companies/(?P<company_id>\d+)/users',
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
