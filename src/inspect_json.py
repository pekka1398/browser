
import json
import sys

def inspect_json(data, indent=0, key_name="ROOT"):
    """
    Recursively inspects JSON data and prints its structure.
    - Limits long strings.
    - Shows list length and inspects the first item only (assuming homogeneity).
    - Handling common types.
    """
    prefix = "  " * indent
    
    if isinstance(data, dict):
        print(f"{prefix}{key_name} (dict, {len(data)} keys)")
        for k, v in data.items():
            inspect_json(v, indent + 1, k)
            
    elif isinstance(data, list):
        if not data:
            print(f"{prefix}{key_name} (list, empty)")
        else:
            print(f"{prefix}{key_name} (list, len={len(data)})")
            # Creating a visual branch explicitly for the items
            # Inspect ONLY the first item as a sample
            inspect_json(data[0], indent + 2, "[0]")
            if len(data) > 1:
                 print(f"{prefix}    ... (and {len(data)-1} more items)")

    else:
        # Primitive types (int, str, bool, None)
        val_str = str(data)
        if len(val_str) > 50:
            val_str = val_str[:50] + "..."
        val_str = val_str.replace('\n', '\\n')
        
        type_name = type(data).__name__
        print(f"{prefix}{key_name}: {val_str} ({type_name})")

def main():
    if len(sys.argv) < 2:
        print("Usage: python inspect_json.py <filename.json>")
        sys.exit(1)
        
    filename = sys.argv[1]
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"🔍 Inspecting Structure of: {filename}\n")
        inspect_json(data)
        
    except FileNotFoundError:
        print(f"❌ File not found: {filename}")
    except json.JSONDecodeError:
        print(f"❌ Invalid JSON format in: {filename}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
