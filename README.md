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

2. Precompute results with specified parameteters city wide.

Computing a score for all the buildings in the city is too slow to live in the request lifecycle. This task can be run to precompute and store the results in the database. Make sure to adjust the parameters inside the file before running it.
`python scripts/precompute_accessibility.py`

## UI

The UI is a simple sinatra server you can find in the `ui` directory.`ui/app.rb` is the server entrypoint. You can start the server by navigating to the ui directory and running the `run.sh` script

