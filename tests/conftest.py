import os
import sys
import pytest

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture(scope="function")
def test_db():
    """Create a test database and clean it up after the test"""
    test_db_path = "test_social_sculptor.db"
    yield test_db_path
    if os.path.exists(test_db_path):
        os.remove(test_db_path) 