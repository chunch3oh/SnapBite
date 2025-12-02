import os
import json
import openai
import logging

# use the OpenAI client for structured parsing
client = openai

from image_analysis import NutritionAnalysis
from nutrition import calculate_bmi, suggest_calories
from pydantic import BaseModel
from typing import List

class MenuItem(BaseModel):
    name: str
    portion_size: str
    calories: str

class MealSuggestion(BaseModel):
    evaluation: str
    issues: List[str]
    next_meal: str
    suggested_menu: List[MenuItem]

# Make sure your OpenAI API key is set as an environment variable: OPENAI_API_KEY
openai.api_key = os.getenv("OPENAI_API_KEY")

MODEL = "gpt-5-mini"
# Define the expected JSON response format
RESPONSE_FORMAT = {
    "evaluation": "string",                   # brief evaluation of current meal
    "issues": ["string"],                     # list of identified nutrition issues
    "next_meal": "string",                    # next meal type ("lunch" or "dinner")
    "suggested_menu": [                       # list of suggested food items
        {
            "name": "string",
            "portion_size": "string",
            "calories": "string"
        }
    ]
}

# Encapsulate suggestion logic into a class
class MealSuggester:
    def __init__(self, api_key: str = None, model: str = MODEL):
        """
        Initialize the MealSuggester with an OpenAI client and model.
        """
        if api_key:
            openai.api_key = api_key
        self.client = client
        self.model = model
        self.response_format = MealSuggestion

    def load_nutrition_analysis(self, json_str: str) -> NutritionAnalysis:
        """
        Parse a NutritionAnalysis object from a JSON string.
        """
        return NutritionAnalysis.model_validate_json(json_str)

    def get_user_profile(self, height: float, weight: float, goal: str) -> tuple:
        """
        Calculate user BMI and recommended daily calories.
        """
        bmi = calculate_bmi(weight, height)
        daily_calories = suggest_calories(weight, goal)
        return bmi, daily_calories

    def generate_suggestion(
        self,
        analysis: NutritionAnalysis,
        current_meal: str,
        height: float,
        weight: float,
        goal: str
    ) -> MealSuggestion:
        """
        Generate a meal suggestion for the next meal using OpenAI API.
        """
        bmi, daily_calories = self.get_user_profile(height, weight, goal)

        system_prompt = (
            "You are a nutrition assistant. Based on the user's height, weight, nutrition goal, "
            "current meal and nutrition analysis, evaluate if the current meal's "
            "macronutrients (protein, carbs, fat) and calories are balanced, "
            "and suggest a menu and portions for the next meal (lunch or dinner)."
        )

        food_list = "\n".join([
            f"- {item.name}, portion size: {item.portion_size}, calories: {item.calories}, "
            f"protein: {item.macronutrients.protein}, carbs: {item.macronutrients.carbs}, "
            f"fat: {item.macronutrients.fat}"
            for item in analysis.food_items
        ])

        user_prompt = (
            f"User profile: height {height} cm, weight {weight} kg, goal {goal}, "
            f"BMI {bmi:.2f}, recommended daily calories {daily_calories:.0f} kcal.\n"
            f"Current meal: {current_meal}\n"
            f"Current meal analysis:\n{food_list}\n"
            "Please provide a nutrition evaluation and suggestion for the next meal."
        )
        user_prompt += "\nPlease format your response as JSON matching the following schema:\n" + json.dumps(RESPONSE_FORMAT, indent=2)

        logging.info("Sending request to OpenAI API for structured response...")
        response = self.client.beta.chat.completions.parse(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format=self.response_format,
            max_completion_tokens=500
        )
        logging.info("Received structured response from OpenAI API")
        return response

if __name__ == "__main__":
    # Demo usage without CLI or Gradio
    suggester = MealSuggester()

    # 1. Load NutritionAnalysis JSON from a file
    try:
        with open("data/analysis.json", "r", encoding="utf-8") as f:
            analysis_json = f.read()
    except FileNotFoundError:
        print("Please create an 'analysis.json' file with your NutritionAnalysis data.")
        exit(1)

    # 2. Parse the analysis and generate a suggestion
    analysis = suggester.load_nutrition_analysis(analysis_json)
    # Example parameters; adjust as needed
    current_meal = "breakfast"
    height = 170.0  # in cm
    weight = 60.0   # in kg
    goal = "維持"

    suggestion = suggester.generate_suggestion(
        analysis=analysis,
        current_meal=current_meal,
        height=height,
        weight=weight,
        goal=goal
    )

    # 3. Print structured suggestion
    try:
        # If suggestion is a Pydantic model with .json() method
        print("\n=== Nutrition Suggestion ===")
        print(suggestion.model_dump_json(indent=2))
    except AttributeError:
        # Otherwise, print raw response
        print("\n=== Nutrition Suggestion ===")
        print(suggestion)
