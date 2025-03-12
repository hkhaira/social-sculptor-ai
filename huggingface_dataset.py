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
            return DatasetDict({
                "linkedin": Dataset.from_dict({"original_text": [], "transformed_text": [], "metadata": []}),
                "twitter": Dataset.from_dict({"original_text": [], "transformed_text": [], "metadata": []}),
                "instagram": Dataset.from_dict({"original_text": [], "transformed_text": [], "metadata": []})
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
        
        # Create new dataset with added example
        new_example = {
            "original_text": [original_text],
            "transformed_text": [transformed_text],
            "metadata": [metadata_str]
        }
        
        # Append to existing dataset
        platform_dataset = self.dataset_dict[platform]
        self.dataset_dict[platform] = Dataset.from_dict({
            **platform_dataset,
            **new_example
        })
        
    def push_to_hub(self):
        """Push the dataset to Hugging Face Hub"""
        self.dataset_dict.push_to_hub(self.repo_name)
