"""
Setup file for the state machine demo server.
This file is used to make the app package importable.
"""

from setuptools import setup, find_packages

setup(
    name="state_machine_demo",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "sqlalchemy",
        "openai",
        "pydantic",
    ],
) 