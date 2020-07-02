### Running Tests

1. Install pytest in the virtual environment:
   ```
   pipenv shell
   pip install pytest
   ```
1. Run tests ignoring the manual tests in the `dev_testing` directory:
   `python -m pytest --ignore='dev_testing'`.