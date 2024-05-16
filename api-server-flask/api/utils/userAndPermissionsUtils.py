from cloudSql import *

import models

def getUserInfo(user_email):
    with engine.connect() as conn:
        stmt = select(models.User).where(models.User.user_email == user_email)
        result = conn.execute(stmt)
        #needs to happen because you can only call result.first() once
        user = result.first()
        if user == None:
            return None
        return user._asdict()

#probably useless function now that userInfo exists but i don't remember wwhat uses it so it sits here
def userExists(user_email):
    with engine.connect() as conn:
        stmt = select(models.User).where(models.User.user_email == user_email)
        result = conn.execute(stmt)
        return result.first() != None

def createNewUser(user_email, name):
    with engine.connect() as conn:
        stmt = insert(models.User).values(
            user_email = user_email,
            name = name
        )
        conn.execute(stmt)
        conn.commit()
    return True

def deleteUser(user_email, proj_id):
    with engine.connect() as conn:
        relationstmt = delete(models.UserProjectRelation).where(
            models.UserProjectRelation.user_email == user_email,
            proj_id == proj_id
        )

        conn.execute(relationstmt)
        conn.commit()
    return True

def getUserProjPermissions(user_email, proj_id):
    with engine.connect() as conn:
        stmt = select(models.UserProjectRelation).where(models.UserProjectRelation.user_email == user_email, models.UserProjectRelation.proj_id == proj_id)
        result = conn.execute(stmt)
        #needs to happen because you can only call result.first() once
        relation = result.first()
        if relation == None:
            return -1
        return relation.permissions

# Find all project relationship models for user email
def getAllUserProjPermissionsForUser(user_email):
    with engine.connect() as conn:
        stmt = select(models.UserProjectRelation).where(models.UserProjectRelation.user_email == user_email)

        result = conn.execute(stmt)

        returnList = []
        for row in result:
            returnList.append(row._asdict())

        return returnList
# Find all project relationship models for project
def getAllUserProjPermissionsForProject(proj_id):
    with engine.connect() as conn:
        stmt = select(models.UserProjectRelation).where(models.UserProjectRelation.proj_id == proj_id)

        result = conn.execute(stmt)

        returnList = []
        for row in result:
            returnList.append(row._asdict())

        return returnList


def setUserProjPermissions(email, proj_id, r, perms):
    try:
        with engine.connect() as conn:
            stmt = insert(models.UserProjectRelation).values(
                    user_email = email,
                    proj_id = proj_id,
                    role = r,
                    permissions = perms
            )
            if(getUserProjPermissions(email, proj_id)) < 0:
                stmt = insert(models.UserProjectRelation).values(
                        user_email = email,
                        proj_id = proj_id,
                        role = r,
                        permissions = perms
                )
            else:
                stmt = update(models.UserProjectRelation).where(
                    models.UserProjectRelation.user_email == email,
                    models.UserProjectRelation.proj_id == proj_id
                ).values(
                    role = r,
                    permissions = perms
                )
            conn.execute(stmt)
            conn.commit()
        return True
    except Exception as e:
        print(e)
        return False

def changeProjectOwner(email, proj_id):
    try:
        with engine.connect() as conn:
            stmt = select(models.Project).where(models.Project.proj_id == proj_id)
            project = conn.execute(stmt).first()
            setUserProjPermissions(project.author_email, proj_id, "Admin", 3)
            setUserProjPermissions(email, proj_id, "Owner", 5)
            stmt = update(models.Project).where(
                    models.Project.proj_id == proj_id
                ).values(
                    author_email = email
                )
            conn.execute(stmt)
            conn.commit()
        return True
    except Exception as e:
        print(e)
        return False
