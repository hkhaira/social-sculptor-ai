from datasets import load_dataset
import json

def load_and_analyze_dataset(repo_name):
    """Load and analyze the dataset from Hugging Face Hub"""
    dataset = load_dataset(repo_name)
    
    stats = {}
    for platform in dataset.keys():
        platform_data = dataset[platform]
        stats[platform] = {
            "total_examples": len(platform_data),
            "avg_original_length": sum(len(text) for text in platform_data["original_text"]) / len(platform_data) if len(platform_data) > 0 else 0,
            "avg_transformed_length": sum(len(text) for text in platform_data["transformed_text"]) / len(platform_data) if len(platform_data) > 0 else 0
        }
    
    return dataset, stats

def prepare_for_fine_tuning(dataset, output_format="jsonl"):
    """Prepare dataset for fine-tuning in various formats"""
    fine_tuning_data = []
    
    for platform in dataset.keys():
        platform_data = dataset[platform]
        for i in range(len(platform_data)):
            # Format depends on the model you'll be fine-tuning
            example = {
                "messages": [
                    {"role": "system", "content": f"You are a content optimizer for {platform}"},
                    {"role": "user", "content": platform_data["original_text"][i]},
                    {"role": "assistant", "content": platform_data["transformed_text"][i]}
                ]
            }
            fine_tuning_data.append(example)
    
    # Save in the specified format
    if output_format == "jsonl":
        with open("fine_tuning_data.jsonl", "w") as f:
            for example in fine_tuning_data:
                f.write(json.dumps(example) + "\n")
    
    return fine_tuning_data
