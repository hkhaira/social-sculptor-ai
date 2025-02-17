from pathlib import Path
from database import Example, init_db

def migrate_existing_examples():
    session = init_db()
    examples_path = Path("data/examples.txt")
    
    if examples_path.exists():
        with open(examples_path, "r", encoding="utf-8") as f:
            examples = f.read().split("\n\n")
            for example in examples:
                if example.strip():
                    session.add(Example(content=example.strip()))
        session.commit()

if __name__ == "__main__":
    migrate_existing_examples()