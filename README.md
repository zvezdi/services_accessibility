## Setup

1. Activate the venv with `source venv_service_accessibility/bin/activate`
2. Run `pip install -r requirements.txt` to ensure all dependencies are installed.
3. Ensure your .env file has the correct DATABASE_URL
4. From the project root, run `python src/main.py` to start the server at http://localhost:8000

## Run the tests

1. First install the project as editable package with `pip install -e .`
2. Run `pytest` from the root of the project
