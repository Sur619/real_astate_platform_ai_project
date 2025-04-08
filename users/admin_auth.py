from fastapi import Depends, HTTPException, status
from users.auth import get_current_user
from users.models import User


async def admin_required(current_user: User = Depends(get_current_user)):
    """
    Dependency to check if the current user belongs to the admin group.
    Raises an HTTPException if the user is not an admin.
    """
    # Check if the user belongs to the admin group
    admin_group = [group for group in current_user.groups if group.name == "admin"]

    if not admin_group:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Admin privileges required"
        )

    return current_user
