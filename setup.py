import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    install_requires=[
        "snowflake==0.6.0",
        "snowflake-snowpark-python[pandas]==1.13.0",
        "importlib_resources==6.3.0"
    ],
    include_package_data=True,
)