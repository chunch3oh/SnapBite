import base64
import requests
from PIL import Image
from io import BytesIO
import json
import gradio as gr
import logging
from openai import OpenAI
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

logging.basicConfig(level=logging.INFO)


# Reference object info (example: standard plate, banana, etc.)
REFERENCE_OBJECT = {
    "name": "standard banana",
    "length_cm": 18.0  # example length of reference item in centimeters
}

class Macronutrient(BaseModel):
    carbs: str
    protein: str
    fat: str

class FoodItem(BaseModel):
    name: str
    portion_size: str
    calories: str
    macronutrients: Macronutrient

class NutritionAnalysis(BaseModel):
    food_items: List[FoodItem]

VISION_MODEL = "gpt-4o-mini"  

def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def call_openai_vision_api(base64_image, reference_info, language="English"):
    logging.info("Sending request to OpenAI API...")
    response = client.beta.chat.completions.parse(
        model=VISION_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    f"You are a professional nutrition analyst AI. Your job is to analyze meal images and return nutritional information in {language}. "
                    "Be precise and concise, and respond in a structured JSON format only."
                )
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            f"This image contains a meal. Estimate the types of food using the reference object ({reference_info['name']}, "
                            f"{reference_info['length_cm']} cm long). Return a structured JSON following this schema:\n\n"
                            "- List of food items\n"
                            "- Each item includes:\n"
                            "  - name\n"
                            "  - portion_size (e.g., 100g or 1/2 of reference)\n"
                            "  - calories (e.g., 230 kcal)\n"
                            "  - macronutrients: carbs, protein, fat (in grams)\n\n"
                            "Avoid any explanatory text, only respond with JSON that fits the expected format."
                        )
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        response_format=NutritionAnalysis,
        max_tokens=1000
    )
    logging.info("Received response from OpenAI API")
    return response

def analyze_image(image_path, language="English"):
    base64_image = encode_image_to_base64(image_path)
    result = call_openai_vision_api(base64_image, REFERENCE_OBJECT, language)

    try:
        structured_output = result.choices[0].message.parsed
        return structured_output
    except Exception as e:
        logging.error("Failed to parse structured output", exc_info=True)
        return {}

def gradio_interface(image, language):
    # Save uploaded image temporarily
    image_path = "temp_uploaded_image.jpg"
    image.save(image_path)
    return analyze_image(image_path, language)

iface = gr.Interface(
    fn=gradio_interface,
    inputs=[gr.Image(type="pil"), 
            gr.Dropdown(
                label="Language",
                choices=[
                    "English (en)",
                    "繁體中文 (zh-tw)",
                    "日本語 (ja)",
                    "Español (es)",
                    "Français (fr)"
                ],
                value="English (en)"
            )],
    outputs="text",
    title="SnapBite: Meal Nutrition Analyzer",
    description="Upload a meal image including a reference object (e.g. a banana) to estimate nutrition info."
)

iface.launch()

if __name__ == "__main__":
    image_file_path = "/mnt/data/1252237D-682C-4E02-B05A-B5310F0534A5.jpeg"
    output = analyze_image(image_file_path)
    print("Structured Nutrition Data:")
    print(output)
