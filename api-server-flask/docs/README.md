
1. activate .venv in the terminal and go back to this directory
2. disable credentials by commenting out lines that open or load from credentials (I did not figure out how to resolve these issues)
3. Type in the terminal `sphinx-apidoc -f -o docs ../api`
4. Type in the terminal `make html`
5. documentation stored in `_build/html/index.html`.
