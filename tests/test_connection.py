import pytest
from pymongo import MongoClient

from database.config import DB_URI


@pytest.fixture(scope="session")
def mongodb():
    uri = DB_URI
    client = MongoClient(uri)
    assert (
        client.admin.command("ping")["ok"] != 0.0
    )  # Check that the connection is okay.
    return client


def test_valid_connection(mongodb):
    """This test will pass if MDB_URI is set to a valid connection string."""
    assert mongodb.admin.command("ping")["ok"] > 0
