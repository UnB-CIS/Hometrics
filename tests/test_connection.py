import pytest
import os
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from database.connection import MongoDBConnection
from database.config import DB_URI

import pytest
import pymongo
import os

@pytest.fixture(scope="session")
def mongodb():
    uri = DB_URI
    client = pymongo.MongoClient(uri)
    assert client.admin.command("ping")["ok"] != 0.0  # Check that the connection is okay.
    return client

def test_valid_connection(mongodb):
    """ This test will pass if MDB_URI is set to a valid connection string. """
    assert mongodb.admin.command("ping")["ok"] > 0