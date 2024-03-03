from django.contrib.auth.models import AnonymousUser
from rest_framework import permissions

from edu.models import Enrollment


class IsTutor(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.status)


class IsAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.author == request.user


class IsAcceptedStudentOrIsAuthor(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if view.action == 'lessons':
            perm = Enrollment.objects.filter(product__title=obj.get('title'), student=request.user).values('permission')
            if perm:
                return True
            print(obj)
            return obj.get('author__username') == request.user.username


class IsAnonymousUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_anonymous
