import os
from abc_project_vars import DIR_PROMPTS
from abc_project_vars import PROMPTS
from base64 import b64encode
from mistralai import Mistral
from typing import Any
from utilities_io import load_file_as_string
from utilities_io import load_json_string

def encode_image( image_path : str) -> str | None :
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

def read_errors( image_path : str) -> str | None :
    """
    Analyze an image using Mistral API to extract error information.
    Args:
        image_path (str): Path to the image file to analyze
    Returns:
        str: Extracted errors
    """
    try:
        # Setup the API key, client and model
        api_key = os.environ.get("MISTRAL_API_KEY")
        if not api_key:
            print("Error: MISTRAL_API_KEY environment variable not set")
            return None
        client = Mistral(api_key=api_key)
        model  = "pixtral-12b-2409"
        # Load agent prompts
        prompt = ''
        for p in PROMPTS :
            prompt_path = os.path.join( DIR_PROMPTS, p)
            prompt += load_file_as_string(prompt_path) + '\n'
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
            messages=messages # type: ignore
        )
        if chat_response and chat_response.choices :
            # Extract the content of the response
            errors_read = str(chat_response.choices[0].message.content)
            errors_obj  = load_json_string(errors_read)
            # The grand finale
            return errors_obj
        else :
            print("No response received from the API")
    # The sad finale: Exception
    except Exception as e:
        print(f"Exception in read_errors: {e}")
    # The sad finale: None
    return None

def write_errors_summary( errors_obj : Any) -> str :
    """Print a summary of the extracted errors."""
    # Get the language and number of messages
    language = errors_obj.get( 'metadata', {}).get( 'language', 'Unknown')
    num_msg  = errors_obj.get( 'metadata', {}).get( 'num_msg', 0)
    # Print the language and number of messages
    output  = ''
    output += f"Language: {language}\n"
    output += f"Number of messages: {num_msg}\n"
    # Print the extracted errors
    if num_msg > 0 and errors_obj.get('data'):
        output += "Extracted Errors:\n"
        for i, msg in enumerate(errors_obj['data'], 1):
            output += f"{i}. {msg}\n"
    # The sad ending: No error messages found
    else:
        output += "No error messages found\n"
    # The grand finale
    return output
