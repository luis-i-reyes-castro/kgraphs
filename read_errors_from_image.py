import os
import sys
from base64 import b64encode
from constants import DIR_AGENT_PROMPTS, AGENT_PROMPTS
from mistralai import Mistral
from utilities_io import load_file_as_string, load_json_string, save_json_file

def encode_image(image_path : str) -> str | None :
    """Encode the image to base64."""
    try:
        with open(image_path, "rb") as image_file:
            return b64encode(image_file.read()).decode('utf-8')
    except FileNotFoundError:
        print(f"Error: The file {image_path} was not found.")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def read_errors( image_path : str,
                 save_results : bool = True,
                 output_dir : str = 'stage_1_results') -> dict | None :
    """
    Analyze an image using Mistral API to extract error information.
    
    Args:
        image_path (str): Path to the image file to analyze
        save_results (bool): Whether to save results to JSON file (default: True)
        output_dir (str): Directory to save results (default: 'stage_1_results')
    
    Returns:
        dict: Dictionary containing the extracted errors and metadata, or None if failed
    """
    try:
        # Setup the API key, client and model
        api_key = os.environ.get("MISTRAL_API_KEY")
        if not api_key:
            print("Error: MISTRAL_API_KEY environment variable not set")
            return None
        client = Mistral(api_key=api_key)
        model  = "pixtral-12b-2409"
        # Load agent prompt
        prompt_path = os.path.join(DIR_AGENT_PROMPTS, AGENT_PROMPTS[0])
        prompt      = load_file_as_string(prompt_path)
        # Encode image as base64
        base64_image = encode_image(image_path)
        if not base64_image :
            return None
        # Define the messages for the chat
        messages = [
        {
        "role": "user",
        "content": [
            {
            "type": "text",
            "text": prompt
            },
            {
            "type": "image_url",
            "image_url": f"data:image/jpeg;base64,{base64_image}" 
            }
        ]
        }
        ]
        # Call the API
        chat_response = client.chat.complete(
            model=model,
            messages=messages  # type: ignore
        )
        if chat_response and chat_response.choices :
            # Extract the content of the response
            extracted_errors = str(chat_response.choices[0].message.content) # type: ignore
            # Parse the JSON response
            error_obj = load_json_string(extracted_errors)
            # Save results if requested
            if save_results:
                # Create output directory if it doesn't exist
                os.makedirs(output_dir, exist_ok=True)
                
                # Generate filename based on image name
                image_name = os.path.basename(image_path)
                fname = os.path.join(output_dir, image_name.replace(".jpg", ".json"))
                save_json_file(fname, error_obj)
                print(f"Results saved to: {fname}")
            # The grand finale
            return error_obj
        else:
            print("No response received from the API")
    # The sad finale: Exception
    except Exception as e:
        print(f"Error calling API: {e}")
    # The sad finale: None
    return None

def print_error_summary( error_obj : dict | None) -> None :
    """Print a summary of the extracted errors."""
    if error_obj is None:
        print("No error data to display")
        return
    # Get the language and number of messages
    language = error_obj.get('metadata', {}).get('language', 'Unknown')
    num_msg  = error_obj.get('metadata', {}).get('num_msg', 0)
    # Print the language and number of messages
    print(f"Language: {language}")
    print(f"Number of messages: {num_msg}")
    # Print the extracted errors
    if error_obj.get('data'):
        print("\nExtracted Errors:")
        for i, msg in enumerate(error_obj['data'], 1):
            print(f"{i}. {msg}")
    # The sad ending: No error messages found
    else:
        print("No error messages found")
    # The grand finale
    return

# Main function
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python read_errors_from_image.py <image_path>")
        sys.exit(1)
    image_path = sys.argv[1]
    result = read_errors(image_path)
    print_error_summary(result)
