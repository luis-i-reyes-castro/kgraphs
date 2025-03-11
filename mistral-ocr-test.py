import base64
import os
from mistralai import Mistral
import prompt_templates as pt

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
IMAGE_DIR = "/home/luis/DJI_AGRAS_LATINO/rc/t40_t50/"
# Spray images
# image_path = IMAGE_DIR + "spray/2023-05-31_09-11-36_i0.jpg"
# image_path = IMAGE_DIR + "spray/2023-09-07_20-38-33_i0.jpg"
# image_path = IMAGE_DIR + "spray/2024-01-11_09-36-34_i0.jpg"
# image_path = IMAGE_DIR + "spray/2023-07-10_14-12-29_i0.jpg"
# image_path = IMAGE_DIR + "spray/2023-07-23_18-29-39_i0.jpg"
# image_path = IMAGE_DIR + "spray/2023-07-25_13-45-14_i0.jpg"
# Prop images
# image_path = IMAGE_DIR + "prop/2023-06-13_16-33-59_i0.jpg"
# image_path = IMAGE_DIR + "prop/2023-09-05_07-13-10_i0.jpg"
# Flight images
# image_path = IMAGE_DIR + "flight/2023-07-22_10-22-35_i0.jpg"
# image_path = IMAGE_DIR + "flight/2023-07-25_11-08-08_i0.jpg"
# image_path = IMAGE_DIR + "flight/2023-08-23_11-05-18_i0.jpg"
image_path = IMAGE_DIR + "flight/2023-08-26_11-53-42_i0.jpg"

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
                "text": pt.prompt2
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
