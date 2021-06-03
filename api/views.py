from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import (CreateModelMixin, ListModelMixin,
                                   UpdateModelMixin)
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from .permissions import IsOwnerOnly, IsOwnerOrReadOnly, IsStuffOnly
from .serializers import (CompanyListSerializer, CompanySerializer,
                          NewsListSerializer, NewsSerializer,
                          ProfileSerializer)
from companies.models import Company


class CompanyViewSet(ModelViewSet):
    queryset = Company.objects.all()
    permission_classes = [IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return CompanyListSerializer
        return CompanySerializer


class NewsViewSet(CreateModelMixin, ListModelMixin, GenericViewSet):
    serializer_class = NewsSerializer
    permission_classes = [IsStuffOnly]

    def get_queryset(self):
        company = get_object_or_404(Company, id=self.kwargs.get('company_id'))
        return company.news.all()

    def perform_create(self, serializer):
        company = get_object_or_404(Company, id=self.kwargs.get('company_id'))
        serializer.save(company=company)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return NewsListSerializer
        return NewsSerializer


class UserViewSet(UpdateModelMixin, ListModelMixin, GenericViewSet):
    serializer_class = ProfileSerializer
    permission_classes = [IsOwnerOnly]

    def get_queryset(self):
        company = get_object_or_404(Company, id=self.kwargs.get('company_id'))
        return company.staff.all()


class JoinTheCompany(GenericAPIView):
    def get(self, request, company_id):
        if not request.user.is_authenticated:
            return Response(
                {'message': 'Please log in to your account.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if request.user.profile.company:
            return Response(
                {'message': 'Your profile is linked to another organization.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        company = get_object_or_404(Company, id=company_id)
        request.user.profile.company = company
        request.user.profile.role = 'user'
        request.user.profile.save()
        return Response(
            {'message': 'Welcome!'},
            status=status.HTTP_200_OK
        )


class LeftTheCompany(GenericAPIView):
    def get(self, request, company_id):
        if not request.user.is_authenticated:
            return Response(
                {'message': 'Please log in to your account.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        company = get_object_or_404(Company, id=company_id)
        if request.user.profile.company != company:
            return Response(
                {'message': 'You are not a member of this organization.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        request.user.profile.company = None
        request.user.profile.role = 'user'
        request.user.profile.save()
        return Response(
            {'message': 'Good luck!'},
            status=status.HTTP_200_OK
        )
