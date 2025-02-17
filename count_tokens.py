import json
import os
import tiktoken

def count_tokens_in_string(string: str, encoding_name: str = "cl100k_base") -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

def analyze_json_files(directory: str) -> dict:
    """
    Analyzes all JSON files in the given directory and returns token counts.
    Returns a dictionary with filenames as keys and token counts as values.
    """
    token_counts = {}
    
    # Walk through all files in directory
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            filepath = os.path.join(directory, filename)
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Count tokens in the raw JSON string
                token_count = count_tokens_in_string(content)
                token_counts[filename] = token_count
                
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")
    
    return token_counts

def main():
    # Get the current directory
    current_dir = os.getcwd()
    
    # Analyze files
    token_counts = analyze_json_files(current_dir)
    
    # Print results
    print("\nToken counts per file:")
    print("-" * 50)
    total_tokens = 0
    
    # Sort alphabetically by filename
    for filename, count in sorted(token_counts.items()):
        print(f"{filename:<40} {count:>8} tokens")
        total_tokens += count
    
    print("-" * 50)
    msg = "Total tokens across all files:"
    print(f"{msg:<40}{total_tokens:>9}")

if __name__ == "__main__":
    main()
