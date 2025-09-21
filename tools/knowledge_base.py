import json

def load_knowledge_from_json(filepath: str) -> dict:
    """
    Reads a JSON file from the given path and loads it into a Python dictionary.
    """
    try:
        # 'with open...' ensures the file is properly closed after reading
        with open(filepath, 'r', encoding='utf-8') as f:
            # json.load() reads a file and parses the JSON data inside it
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Knowledge base file not found at {filepath}")
        return {}
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from the file at {filepath}. Check for syntax errors.")
        return {}

# --- LOAD THE KNOWLEDGE BASE ---
# This line runs once when the server starts.
# It reads your .txt file and stores the data in the KNOWLEDGE_BASE variable.
KNOWLEDGE_BASE = load_knowledge_from_json('data/knowledge_base.txt')

def search_knowledge_base(city: str, topic: str) -> str:
    """
    Searches the in-memory knowledge base (loaded from the JSON file)
    for a specific city and topic.
    """
    # This function now searches the data that was loaded from your file
    city_knowledge = KNOWLEDGE_BASE.get(city.lower(), {})
    return city_knowledge.get(topic.lower(), "No specific information found on that topic.")