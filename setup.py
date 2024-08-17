from setuptools import setup, find_packages

setup(
    name="service_accessibility",
    version="0.1.0",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "geopandas",
        "sqlalchemy",
        "geoalchemy2",
        "psycopg2-binary",
        "fastapi",
        "uvicorn",
        "python-dotenv",
    ],
)