"""Test environment must be set BEFORE any app module is imported:
tests run against a throwaway data dir and the offline mock embedder.
"""

import os
import tempfile

os.environ["DATA_DIR"] = tempfile.mkdtemp(prefix="hml-test-")
os.environ["EMBEDDING_PROVIDER"] = "mock"

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as test_client:
        yield test_client
