from datasets import Dataset, DatasetDict
from huggingface_hub import HfApi, login
import os
import pandas as pd
from datetime import datetime
import json

class HuggingFaceDatasetManager:
    def __init__(self, token=None, repo_name=None):
        self.token = token or os.getenv("HUGGINGFACE_TOKEN")
        self.repo_name = repo_name or os.getenv("DATASET_REPO_NAME")
        self.api = HfApi()
        
        if self.token:
            login(token=self.token)
            
        # Create/load dataset structure
        self.dataset_dict = self._init_dataset()
    
    def _init_dataset(self):
        """Initialize or load existing dataset"""
        try:
            # Try to load existing dataset
            from datasets import load_dataset
            dataset_dict = load_dataset(self.repo_name)
            return dataset_dict
        except Exception:
            # Create new dataset structure if not exists
            # Ensure all datasets have the same feature structure with non-null values
            empty_dataset = {
                "original_text": [], 
                "transformed_text": [], 
                "metadata": []
            }
            
            return DatasetDict({
                "linkedin": Dataset.from_dict(empty_dataset),
                "twitter": Dataset.from_dict(empty_dataset),
                "instagram": Dataset.from_dict(empty_dataset)
            })
    
    def add_transformation(self, platform, original_text, transformed_text, metadata=None):
        """Add a transformation to the dataset"""
        platform = platform.lower()
        if platform not in self.dataset_dict:
            raise ValueError(f"Unknown platform: {platform}")
            
        # Prepare metadata
        if metadata is None:
            metadata = {}
            
        metadata.update({
            "timestamp": datetime.now().isoformat(),
            "platform": platform,
        })
        
        # Convert metadata to string for storage
        metadata_str = json.dumps(metadata)
        
        # Get existing data
        current_dataset = self.dataset_dict[platform]
        
        # Create new dataset with the added example
        new_dataset = Dataset.from_dict({
            "original_text": current_dataset["original_text"] + [original_text],
            "transformed_text": current_dataset["transformed_text"] + [transformed_text],
            "metadata": current_dataset["metadata"] + [metadata_str]
        })
        
        # Update the dataset
        self.dataset_dict[platform] = new_dataset
        
        # Ensure all platforms have the same feature structure
        # This is important when one platform has data but others don't
        for other_platform in self.dataset_dict:
            if other_platform != platform and len(self.dataset_dict[other_platform]) == 0:
                # Initialize empty platform datasets with at least one dummy row to establish types
                self.dataset_dict[other_platform] = Dataset.from_dict({
                    "original_text": [""],  # Empty string instead of null
                    "transformed_text": [""],
                    "metadata": ["{}"]
                })
        
    def push_to_hub(self):
        """Push the dataset to Hugging Face Hub"""
        if not self.token:
            raise ValueError("Hugging Face token is required to push to hub. Set HUGGINGFACE_TOKEN in your environment.")
        
        if not self.repo_name:
            raise ValueError("Repository name is required to push to hub. Set DATASET_REPO_NAME in your environment.")
        
        # Ensure we're logged in
        login(token=self.token)
        
        try:
            # Push the dataset to the hub
            self.dataset_dict.push_to_hub(
                self.repo_name,
                private=False,
                token=self.token
            )
            return True
        except Exception as e:
            print(f"Error pushing to Hugging Face Hub: {str(e)}")
            raise
