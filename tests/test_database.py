import unittest
import os
import uuid
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import (
    Base, LinkedInExample, TwitterExample, InstagramExample,
    LinkedInTransformation, TwitterTransformation, InstagramTransformation
)

class TestDatabase(unittest.TestCase):
    def setUp(self):
        # Create a test database
        self.test_db_path = "test_social_sculptor.db"
        self.engine = create_engine(f'sqlite:///{self.test_db_path}')
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
    
    def tearDown(self):
        # Clean up the test database
        self.session.close()
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
    
    def test_linkedin_example_creation(self):
        # Test creating a LinkedIn example
        example = LinkedInExample(
            id=str(uuid.uuid4()),
            content="Test LinkedIn content"
        )
        self.session.add(example)
        self.session.commit()
        
        # Retrieve and verify
        retrieved = self.session.query(LinkedInExample).first()
        self.assertEqual(retrieved.content, "Test LinkedIn content")
        self.assertIsInstance(retrieved.created_at, datetime)
    
    def test_twitter_example_creation(self):
        # Test creating a Twitter example
        example = TwitterExample(
            id=str(uuid.uuid4()),
            content="Test Twitter content"
        )
        self.session.add(example)
        self.session.commit()
        
        # Retrieve and verify
        retrieved = self.session.query(TwitterExample).first()
        self.assertEqual(retrieved.content, "Test Twitter content")
        self.assertIsInstance(retrieved.created_at, datetime)
    
    def test_instagram_example_creation(self):
        # Test creating an Instagram example
        example = InstagramExample(
            id=str(uuid.uuid4()),
            content="Test Instagram content"
        )
        self.session.add(example)
        self.session.commit()
        
        # Retrieve and verify
        retrieved = self.session.query(InstagramExample).first()
        self.assertEqual(retrieved.content, "Test Instagram content")
        self.assertIsInstance(retrieved.created_at, datetime)
    
    def test_linkedin_transformation_creation(self):
        # Test creating a LinkedIn transformation
        transformation = LinkedInTransformation(
            id=str(uuid.uuid4()),
            original_text="Original LinkedIn text",
            transformed_text="Transformed LinkedIn text"
        )
        self.session.add(transformation)
        self.session.commit()
        
        # Retrieve and verify
        retrieved = self.session.query(LinkedInTransformation).first()
        self.assertEqual(retrieved.original_text, "Original LinkedIn text")
        self.assertEqual(retrieved.transformed_text, "Transformed LinkedIn text")
        self.assertIsInstance(retrieved.created_at, datetime)
    
    def test_twitter_transformation_creation(self):
        # Test creating a Twitter transformation
        transformation = TwitterTransformation(
            id=str(uuid.uuid4()),
            original_text="Original Twitter text",
            transformed_text="Transformed Twitter text"
        )
        self.session.add(transformation)
        self.session.commit()
        
        # Retrieve and verify
        retrieved = self.session.query(TwitterTransformation).first()
        self.assertEqual(retrieved.original_text, "Original Twitter text")
        self.assertEqual(retrieved.transformed_text, "Transformed Twitter text")
        self.assertIsInstance(retrieved.created_at, datetime)
    
    def test_instagram_transformation_creation(self):
        # Test creating an Instagram transformation
        transformation = InstagramTransformation(
            id=str(uuid.uuid4()),
            original_text="Original Instagram text",
            transformed_text="Transformed Instagram text"
        )
        self.session.add(transformation)
        self.session.commit()
        
        # Retrieve and verify
        retrieved = self.session.query(InstagramTransformation).first()
        self.assertEqual(retrieved.original_text, "Original Instagram text")
        self.assertEqual(retrieved.transformed_text, "Transformed Instagram text")
        self.assertIsInstance(retrieved.created_at, datetime)

if __name__ == '__main__':
    unittest.main() 