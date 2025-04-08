from users.models import User


def is_in_group(user: User, group_name: str) -> bool:
    """
    Check if a user belongs to a specific group.

    Args:
        user: The user object to check
        group_name: The name of the group to check for

    Returns:
        bool: True if the user belongs to the group, False otherwise
    """
    return any(group.name == group_name for group in user.groups)


def is_admin(user: User) -> bool:
    """
    Check if a user has admin privileges.

    Args:
        user: The user object to check

    Returns:
        bool: True if the user is an admin, False otherwise
    """
    return is_in_group(user, "admin")