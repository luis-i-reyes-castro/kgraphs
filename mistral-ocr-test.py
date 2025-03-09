import base64
import os
from mistralai import Mistral

def encode_image(image_path):
    """Encode the image to base64."""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except FileNotFoundError:
        print(f"Error: The file {image_path} was not found.")
        return None
    except Exception as e:  # Added general exception handling
        print(f"Error: {e}")
        return None

# Path to your image
# image_path = "/home/luis/DJI_AGRAS_LATINO/rc/t40_t50/spray/2023-05-31_09-11-36_i0.jpg"
image_path = "/home/luis/DJI_AGRAS_LATINO/rc/t40_t50/spray/2023-09-07_20-38-33_i0.jpg"

# Getting the base64 string
base64_image = encode_image(image_path)

api_key = os.environ["MISTRAL_API_KEY"]
client = Mistral(api_key=api_key)
model = "pixtral-12b-2409"

# Define the messages for the chat
messages = [
    {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": "The attached image is a photo of a drone remote control screen. Zero, one or more error messages may be visible inside red boxes, either in English or Spanish (but only in one language). Please list the error messages in JSON format according to the following template: [ {'language': fill language, 'num_messages': fill number of messages (zero if none)}, {'message_text': fill first error message text}, ... ]."
            },
            {
                "type": "image_url",
                "image_url": f"data:image/jpeg;base64,{base64_image}" 
            }
        ]
    }
]

# Get the chat response
chat_response = client.chat.complete(
    model=model,
    messages=messages
)

# Print the content of the response
print(chat_response.choices[0].message.content)
