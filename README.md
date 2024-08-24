## Setup

1. Activate the venv with `source venv_service_accessibility/bin/activate`
2. Run `pip install -r requirements.txt` to ensure all dependencies are installed.
3. Ensure your .env file has the correct DATABASE_URL
4. From the project root, run `python src/run.py` to start the server at http://localhost:8000

## Run the tests

1. First install the project as editable package with `pip install -e .`
2. Run `pytest` from the root of the project

## Tasks

1. Prebuild the pedestian network with residential buildings and POIs added to it.

The building of the graph is too slow to live in the request lifecycle. This task can be run to rebuild the graph from the database.
`python scripts/prebuild_network.py`
