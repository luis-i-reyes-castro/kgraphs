from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
import base64
import os

# Function to encode image as Base64
def encode_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")

# Specify image path
image_path = "/home/luis/DJI_AGRAS_LATINO/rc/t40_t50/spray/2023-05-31_09-11-36_i0.jpg"

# Encode the image
image_base64 = encode_image(image_path)

# Initialize GPT-4 Vision model in LangChain
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Prepare image input as a message
image_message = {
    "type": "image_url",
    "image_url": f"data:image/jpeg;base64,{image_base64}"
}

# Define conversation
messages = [
    HumanMessage(
        content=[image_message,
                 {"type": "text",
                  "text": "The attached image is a photo of a drone remote control screen. One or more error messages may be visible. These error messages are usually inside red boxes. The contents of the error messages are either in English or Spanish. Please describe the error messages in JSON format, with the following fields: 'message_text', 'message_language'."}])
]

# Get response from the model
response = llm.invoke(messages)

# Print the response
print(response.content)

# import openai
# import os

# openai.api_key = os.getenv("OPENAI_API_KEY")

# response = openai.chat.completions.create(
#     model="gpt-3.5-turbo",
#     messages=[{"role": "user", "content": "Hello!"}]
# )

# print(response)
