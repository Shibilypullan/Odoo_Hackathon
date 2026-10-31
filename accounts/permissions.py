from django.core.exceptions import PermissionDenied


def is_admin(user):
    return (
        user.is_authenticated
        and user.role == 'admin'
        and user.is_superuser
    )


def is_staff_member(user):
    return (
        user.is_authenticated
        and user.role == 'staff'
        and user.is_staff
        and not user.is_superuser
    )


def is_customer(user):
    return (
        user.is_authenticated
        and user.role == 'customer'
    )


def require_admin(user):
    if not is_admin(user):
        raise PermissionDenied


def require_staff_or_admin(user):
    if not (is_admin(user) or is_staff_member(user)):
        raise PermissionDenied