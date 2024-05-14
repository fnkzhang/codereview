export function IsUserAllowedToShare(userPermissionLevel) {
    if (userPermissionLevel < 3)
        return false;

    return true;
}
