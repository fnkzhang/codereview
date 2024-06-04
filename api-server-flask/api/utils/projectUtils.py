from cloudSql import *
from utils.folderUtils import *
from utils.documentUtils import *
from utils.snapshotUtils import * 
from utils.miscUtils import *
from utils.commitUtils import *
import models

def getProjectInfo(proj_id):
    '''
    **Explanation:**
        Gets a project's information
    **Args:**
        -proj_id (int): id of the document
    **Returns:**
        -foundProject (dict): A Project object as a dict
    '''
    with engine.connect() as conn:
        stmt = select(models.Project).where(models.Project.proj_id == proj_id)
        foundProject = conn.execute(stmt).first()
        if foundProject == None:
            return None
        return foundProject._asdict()

def createNewProject(proj_name, owner):
    '''
    **Explanation:**
        Creates a new project with an initial committed commit
    **Args:**
        -proj_name (str): name of the project
        -owner (str): email of the creator of the project
    **Returns:**
        -pid (int): id of the newly created project
    '''
    pid = createID()
    with engine.connect() as conn:
        projstmt = insert(models.Project).values(
                proj_id = pid,
                name = proj_name,
                author_email = owner,
        )
        relationstmt = insert(models.UserProjectRelation).values(
                user_email = owner,
                proj_id = pid,
                role = "Owner",
                permissions = 5
        )
        conn.execute(projstmt)
        conn.execute(relationstmt)
        conn.commit()
    return pid

def purgeProjectUtil(proj_id):
    '''
    **Explanation:**
        Deletes a project from the database entirely. This also deletes associated commits, documents, folders, snapshots, and comments.
    **Args:**
        -proj_id (int): id of the project to delete
    **Returns:**
        -success (bool): success
        -error message (str): if there was an error, returns the message, if not, returns None
    '''
    try:
        threads = []
        with engine.connect() as conn:
            commits = getAllProjectCommits(proj_id)
            for commit in commits:
                thread = threading.Thread(target=deleteCommit, kwargs={"commit_id":commit["commit_id"]})
                thread.start()
                threads.append(thread)
            stmt = delete(models.Project).where(models.Project.proj_id == proj_id)
            conn.execute(stmt)
            stmt = delete(models.UserProjectRelation).where(models.UserProjectRelation.proj_id == proj_id)
            conn.execute(stmt)
            conn.commit()
            for thread in threads:
                thread.join()
        return True, "No Error"
    except Exception as e:
        return False, e

def renameProjectUtil(proj_id, proj_name):
    '''
    **Explanation:**
        Renames a project
    **Args:**
        -project_id (int): id of the project
        -proj_name (str): new name of the item
    **Returns:**
        -Success (bool): whether or not it succeeded
        -Error message (str)
    '''
    try:
        with engine.connect() as conn:
            stmt = (update(models.Project)
                .where(models.Project.proj_id == proj_id)
                .values(name=proj_name)
                )
            conn.execute(stmt)
            conn.commit()
        return True, "No Error"
    except Exception as e:
        return False, e
    
# Returns Array of Dictionaries
def getAllProjectCommits(proj_id):
    '''
    **Explanation:**
        Gets all of the projects's commits in order of when they were committed
    **Args:**
        -proj_id (int): id of the project
    **Returns:**
        -listOfCommits (list): list of Commit objects as dicts
    '''
    with engine.connect() as conn:
        stmt = select(models.Commit).where(models.Commit.proj_id == proj_id).order_by(models.Commit.date_created.asc())
        foundCommits = conn.execute(stmt)

        listOfCommits = []

        for row in foundCommits:
            listOfCommits.append(row._asdict())
        return listOfCommits

# Returns Array of Dictionaries
def getAllCommittedProjectCommitsInOrder(proj_id):
    '''
    **Explanation:**
        Gets all of the projects's commited commits in order of when they were committed
    **Args:**
        -proj_id (int): id of the project
    **Returns:**
        -listOfCommits (list): list of Commit objects as dicts
    '''
    with engine.connect() as conn:
        stmt = select(models.Commit).where(models.Commit.proj_id == proj_id, models.Commit.date_committed != None).order_by(models.Commit.date_committed.asc())
        foundCommits = conn.execute(stmt)

        listOfCommits = []

        for row in foundCommits:
            listOfCommits.append(row._asdict())

        return listOfCommits

def getProjectLastCommittedCommit(proj_id):
    '''
    **Explanation:**
        Gets the projects's latest commited commits
    **Args:**
        -proj_id (int): id of the project
    **Returns:**
        -commit (dict): latest Commit object as a dict
    '''
    try:
        return getAllCommittedProjectCommitsInOrder(proj_id)[-1]
    except Exception as e:
        print(e)
        return None

def getUserWorkingCommitInProject(proj_id, email):
    '''
    **Explanation:**
        Gets a user's working commit for a project
    **Args:**
        -proj_id (int): id of the project
        -email (int): user's email
    **Returns:**
        -commit (dict): the user's working Commit object as a dict
    '''
    with engine.connect() as conn:
        stmt = select(models.Commit).where(models.Commit.proj_id == proj_id, models.Commit.author_email == email, models.Commit.date_committed == None)
        commit = conn.execute(stmt).first()
        if commit == None:
            return None
        return commit._asdict()

