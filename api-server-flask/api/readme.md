## How to run the flask development server

In the codereview/api-server-flask/api/ folder, run 

    flask --app flaskApi.py run --debug

It is now running on port 5000.

## Data Models (found in models.py)

### User

A representation of a user. Users can make projects, add and edit documents, and create comments.

user_email (str) : A user's email address

name (str) : A user's name

date_joined (datetime) : Date the user joined

github_token (str) : Github token associated with user

### Project

A collection of associated files, similar to a Github repository. Projects can have batch changes created on them, which will allow users to see the evolution of the project over time. When a project is deleted, all associated commits, documents, folders, snapshots, and comments will be deleted.

proj_id (int) : Id of the project

name (str) : Name of a project)

author_email (str) : Owner of the project

date_created (datetime) : Date the project was created

[Unfunctional] date_modified (datetime) : Date the project was last modified

### Commit

A representation of versions of a project, which allow for batch changes to the project. Commits are private to the author when first created, and must be committed in order for other users to see them. Users can have one set of private batch changes in a project at a time. Each commit contains a set of items (folders and documents) which shows the version of the project during that commit. These items can exist through multiple commits, but can have different locations, names, and for documents, contents, on each commit. When a project is first made, a commit is automatically created and committed. The contents of this commit can either be empty, if you just make an empty project, or have the contents of a Github repository, if imported. Each commit has a root folder, which is the top level folder for all the files. This root folder will generally be the same folder throughout the entire project, unless an entirely new commit with no parent is created after the initial commit.

author_email (str) : Author of the changes

name (str) : Name of the commit

commit_id (int) : Id of the commit

proj_id (int) : Id of the project that the changes belong to

date_created (datetime) : Date the commit was created

date_committed (datetime) : Date the commit was committed and made public to other users

root_folder (int) : The root folder id in this set of changes

last_commit (int) : The commit id of the commit this new set of changes branches from

state (Enum; open, reviewed, approved, closed) : The current state of the commit

is_approved (bool) : Whether or not the commit is approved or not (Can be fully replaced with state in the future)

approved_count (int) : The amount of reviewers that have approved of the batch changes

### Folder

Representation of a folder item in a filesystem. Can contain other items, such as documents and folders. In order to determine what folders items belong to in each, they have a parent_folder variable in ItemCommitLocation. All folders outside of root folders must exist in another folder to be accessed properly.

folder_id (int) : Id of the folder

associated_proj_id (int) = Id of the project the folder is associated with

og_commit_id (int) = Original commit the folder was created on

date_created (datetime) : Date the folder was created

[Unfuntional] date_modified (datetime) : Date the folder was modified

### Document

Representation of a document item in a filesystem. Documents can have different associated snapshots on different commits, which allow for version control. Documents must exist within a folder to be accessed properly.

doc_id (int) : Id of the document

associated_proj_id (int) : Id of the project the document is associated with

og_commit_id (int) : Original commit the document was created on

date_created (datetime) : Date the document was created

[Unfuntional] date_modified (datetime) : Date the document was modified

is_reviewed (bool) : Whether or not the document has been reviewed

### Snapshot

Representation of a version of a document. These are what actually are connected to the contents found in uploaded or imported files. Id is associated with a blob on Google Buckets which contains the contents of the snapshot. Multiple snapshots can be associated with the same document, but for each specific commit, there is a 1-1 relationship between a document and a snapshot. Snapshots can generally be made only on a user's working (or private) commit, and when a snapshot is created, it overrides the previous snapshot relation between the document and the commit. 

snapshot_id (int) : Id of the snapshot

associated_doc_id (int) : Id of the document the snapshot is associated with

og_commit_id (int) : Original commit the snapshot was created on

date_created (datetime) : Date the snapshot was created

[Should be deleted] date_modified (datetime) : Date the snapshot was modified

### Comment

Representation of a comment. Comments are associated with specific snapshots, and are also associated with a specific location on that snapshot. They're basically Google Docs comments. Comments can also be resolved, signifying that the issue described in the comment is no longer relevant. Each comment also tracks its author, which allows for users to resolve comments properly. Comments, through the frontend, can also be used to create an LLM suggestion.

author_email (str) : Creator of the comment

comment_id (int) : Id of the comment

snapshot_id (int) : Id of the snapshot the comment is associated with

content (str) : The content of the comment

reply_to_id (id) : Id of the comment that this comment is replying to; if a top level comment, the value is 0

date_created (datetime) : Date the comment was created

[Unfunctional] date_modified (datetime) : Date the comment was modified

highlight_start_x (int) : The row that the location the comment is referring to starts on

highlight_start_y = (int) : The column that the location the comment is referring to starts on

highlight_end_x = (int) : The row that the location the comment is referring to ends on

highlight_end_y = (int) : The column that the location the comment is referring to ends on

is_resolved (bool) : Whether or not the comment is resolved

### UserProjRelation

The relation betweeen a user and a project. The permissions value dictates what actions a user can make on a project. Note that currently the frontend does not utilize any of these, and only uses permission levels 3 and 5. In most routes, the relation between the user and project is checked so that only users with valid permissions can enact the route action.

user_email (str) : The user in the relationship

proj_id (int) : The project in the relationship

role (str) : The role the user has in the project. This is mostly decorative

permissions (int) : The level of permissions a user has in a project.

   - 0 : Viewing. The user can view the project
   - 1 : Commenting. The user can make comments
   - 2 : Editor. The user can edit documents directly
   - 3 : Sharing Privileges. The user can share the project with other users
   - 4 : Nothing!
   - 5 : Owner. The user can delete the project.

### ItemCommitLocation

Where an item (folder or document) is located within a commit. This allows tracking of the movement and renaming of items across different commits. If an ItemCommitLocation does not exist for an item on a commit, it is treated as if it does not exist on a commit.

item_id (int) : Id of the item

parent_folder (int) : The folder the item is located in in the commit

commit_id (int) : The commit this location takes place in

name (str) : The name of the item in the commit

is_folder (bool) : Whether or not the item is a folder or not. True for folder, False for document.

### CommitDocumentSnapshotRelation

What version (snapshot) a document was associated with during a specific commit. These are used to access the correct snapshots of documents. A CommitDocumentSnapshotRelation must exist for every document that has an ItemCommitLocation. 

doc_id (int) : Id of the document

commit_id (int) : Id of the commit

snapshot_id (int) : Id of the snapshot

### UserUnseenSnapshot

If this exists within the database, it means that the user has not seen the specific snapshot. Only populated when the user is added to the project the snapshot is located in. When a new snapshot is created, a UserUnseenSnapshot for that snapshot is created for every user that has permissions for project. When a new user is added, a UserUnseenSnapshot is created for every snapshot for them.

snapshot_id (int) : Id of the snapshot

user_email (str) : Email of the user

### UserUnseenComment

If this exists within the database, it means that the user has not seen the specific comment. Only populated when the user is added to the project the comment is located in. When a new comment is created, a UserUnseenComment for that comment is created for every user that has permissions for project. When a new user is added, a UserUnseenComment is created for every comment for them.

comment_id (int) : Id of the comment

user_email (str) : Email of the user
