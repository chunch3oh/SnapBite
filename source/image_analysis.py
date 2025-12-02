import base64
import requests
from PIL import Image
from io import BytesIO
import json
import logging
import gradio as gr
from openai import OpenAI, OpenAIError
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
    "name": "AirPods Pro 2",
    "length_cm": 6.06  # example length of reference item in centimeters
}

MAX_COMPLETION_TOKENS = 600


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

VISION_MODEL = "gpt-4o-mini"  # vision-capable, lighter output

class Analyst:
    def __init__(self, api_key: str = None, reference_object: dict = REFERENCE_OBJECT, vision_model: str = VISION_MODEL, language: str = "zh-TW"):
        # Initialize the OpenAI client and analysis settings
        self.api_key = api_key or OPENAI_API_KEY
        self.client = OpenAI(api_key=self.api_key)
        self.reference_object = reference_object
        self.vision_model = vision_model
        self.language = language

    def encode_image_to_base64(self, image_path: str) -> str:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    def _build_messages(self, base64_image: str, concise: bool = False):
        user_instruction = (
            f"Estimate foods in the photo using reference object {self.reference_object['name']} "
            f"({self.reference_object['length_cm']} cm). Return JSON with food_items: "
            "[{name, portion_size (e.g. 100g or 1/2 reference), calories (e.g. 230 kcal), "
            "macronutrients: {carbs, protein, fat} in grams}]. No extra text."
        )

        if concise:
            user_instruction += (
                " Limit to 3 items max, keep portion_size/calories/macros short integers or whole numbers."
            )

        return [
            {
                "role": "system",
                "content": (
                    "You are a professional nutrition analyst AI. Analyze meal images and return nutritional information in Traditional Chinese (zh-TW). "
                    "All text values (food names, units) must be zh-TW. Be precise and concise, and respond in a structured JSON format only."
                )
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": user_instruction
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ]

    def call_openai_vision_api(self, base64_image: str):
        logging.info("Sending request to OpenAI API...")
        messages = self._build_messages(base64_image)
        try:
            response = self.client.beta.chat.completions.parse(
                model=self.vision_model,
                messages=messages,
                response_format=NutritionAnalysis,
                max_completion_tokens=MAX_COMPLETION_TOKENS
            )
            logging.info("Received response from OpenAI API")
            return response
        except OpenAIError:
            logging.exception("OpenAI API call failed")
            return None

    def analyze_image(self, image_path: str) -> dict:
        base64_image = self.encode_image_to_base64(image_path)
        result = self.call_openai_vision_api(base64_image)
        if not result:
            return {}
        try:
            structured_output = result.choices[0].message.parsed
            if hasattr(structured_output, "model_dump"):
                return structured_output.model_dump()
            return structured_output
        except Exception as e:
            logging.error("Failed to parse structured output", exc_info=True)
            return {}

    def gradio_interface(self, image, language: str = None):
        if language:
            self.language = language
        image_path = "temp_uploaded_image.jpg"
        image.save(image_path)
        return self.analyze_image(image_path)
    
    def get_reference_object(self) -> dict:
        """
        Return the reference object information used for analysis.
        """
        return self.reference_object

if __name__ == "__main__":
    # Example usage
    analyst = Analyst()
    image_path = "example_meal.jpg"  # replace with your image file path
    result = analyst.analyze_image(image_path)
    print("Nutrition Analysis Result:")
    print(result)

    # Uncomment the lines below to launch a Gradio UI for interactive use
    # import gradio as gr
    # gr.Interface(
    #     fn=Analyst().gradio_interface,
    #     inputs=gr.Image(type="pil"),
    #     outputs="json",
    #     title="Meal Nutrition Analyzer"
    # ).launch()
