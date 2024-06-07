## How to run the flask development server

In the codereview/api-server-flask/api/ folder, run 

    flask --app flaskApi.py run --debug

It is now running on port 5000.

## Data Models (found in models.py)

### User

A representation of a user.

user_email (str) : A user's email address

name (str) : A user's name

date_joined (datetime) : Date the user joined

github_token (str) : Github token associated with user

### Project

A collection of associated files, similar to a Github repository.

proj_id (int) : Id of the project

name (str) : Name of a project)

author_email (str) : Owner of the project

date_created (datetime) : Date the project was created

[Unfunctional] date_modified (datetime) : Date the project was last modified

### Commit

A representation of batch changes. Changes are private to the author when first created, and must be committed in order for other users to see them.

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

Representation of a folder item in a filesystem. Can contain other items, such as documents and folders.

folder_id (int) : Id of the folder

associated_proj_id (int) = Id of the project the folder is associated with

og_commit_id (int) = Original commit the folder was created on

date_created (datetime) : Date the folder was created

[Unfuntional] date_modified (datetime) : Date the folder was modified

### Document

Representation of a document item in a filesystem. Documents can have different associated snapshots on different commits, which allow for version control.

doc_id (int) : Id of the document

associated_proj_id (int) : Id of the project the document is associated with

og_commit_id (int) : Original commit the document was created on

date_created (datetime) : Date the document was created

[Unfuntional] date_modified (datetime) : Date the document was modified

is_reviewed (bool) : Whether or not the document has been reviewed

### Snapshot




