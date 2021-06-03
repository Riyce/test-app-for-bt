from rest_framework import permissions

from companies.models import Company


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == 'POST':
            return (
                request.user.is_authenticated and
                request.user.profile.is_owner
            )
        return True

    def has_object_permission(self, request, view, obj):
        if request.method == 'DELETE':
            return obj.owner == request.user
        if request.method == 'PUT' or request.method == 'PATCH':
            return request.user.is_authenticated and (
                obj.owner == request.user or (
                    request.user.profile.is_moderator and
                    request.user.profile.company == obj
                )
            )
        return True


class IsStuffOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        company_id = request.parser_context.get('kwargs')['company_id']
        company = Company.objects.get(id=company_id)
        if request.method != 'GET':
            return (request.user.is_authenticated and (
                company.owner == request.user or (
                    request.user.profile.is_moderator and
                    request.user.profile.company == company
                )
            ))
        return True


class IsOwnerOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        company_id = request.parser_context.get('kwargs')['company_id']
        company = Company.objects.get(id=company_id)
        return company.owner == request.user
