/**
 *  Given a permission level, indicates if the user is allowed to share the project.
 */
export function IsUserAllowedToShare(userPermissionLevel) {
    if (userPermissionLevel < 3)
        return false;

    return true;
}
