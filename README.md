## Code Review Website
A web site that can manage code reviews. To allow for ease of use, it shows a diff view for two versions of a file,

and allows for comments on highlighted sections of text. Reviewers can propose their own changes that the original 

author can either accept or reject on top of making comment suggestions.

## Initialization
### React
With Node.js installed, move to the react directory folder and perform

npm install 



### Flask
To Prepare for flask make sure to set up a python virtual environment

First go back to the root directory of the project

create a python virtual environment if not already there:

python -m venv .venv

To activate, type:

    .venv/Scripts/activate
(Make sure scripts are allowed on the machine)

One the virtual environment is activated install the required libraries by performing 

pip install -r requirements.txt
