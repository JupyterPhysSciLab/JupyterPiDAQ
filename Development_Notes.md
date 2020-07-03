### Running Tests

1. Install updated pytest in the virtual environment:
   ```
   pipenv shell
   pip install -U pytest
   ```
1. Run tests ignoring the manual tests in the `dev_testing` directory:
   `python -m pytest --ignore='dev_testing'`.
   
### Building PyPi package

1. Make sure to update the version number in setup.py first.
1. Install updated  setuptools and twine in the virtual environment:
   ```
   pipenv shell
   pip install -U setuptools wheel twine
   ```
1. Build the distribution `python -m setup sdist bdist_wheel`.
1. Test it on `test.pypi.org`.
    1. Upload it (you will need an account on test.pypi.org):
       `python -m twine upload --repository testpypi dist/*`.
    1. Create a new virtual environment and test install into it:
        ```
        exit # to get out of the current environment
        cd <somewhere>
        mkdir <new virtual environment>
        cd <new directory>
        pipenv shell #creates the new environment and enters it.
        pip install -i https://test.pypi.org/..... # copy actual link from the
                                                   # repository on test.pypi.
        ```