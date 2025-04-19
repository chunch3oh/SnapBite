import json
import matplotlib.pyplot as plt

class Visualizer:
    """
    Encapsulates methods for loading nutrition logs and generating visualizations.
    """
    def load_daily_log(self, filename="data/daily_log.json"):
        """
        Load the daily nutrition log from JSON.
        Expected format: 
        [
          {
            "date": "YYYY-MM-DD",
            "meals": [
              {
                "meal_type": "breakfast",
                "calories": number,
                "macros": {"protein": number, "carbs": number, "fat": number}
              },
              ...
            ]
          },
          ...
        ]
        """
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Ensure we return a list of logs
        return data if isinstance(data, list) else [data]

    def visualize_daily_total_calories(self, daily_logs):
        """
        Line chart of total daily calories across multiple days.
        """
        dates = [d["date"] for d in daily_logs]
        totals = [sum(m["calories"] for m in d["meals"]) for d in daily_logs]

        plt.figure()
        plt.plot(dates, totals, marker="o")
        plt.title("Total Daily Calories Over Days")
        plt.xlabel("Date")
        plt.ylabel("Calories")
        plt.tight_layout()
        plt.show()

    def visualize_calories(self, meals):
        """
        Bar chart of calories per meal.
        """
        meal_types = [m["meal_type"] for m in meals]
        calories = [m["calories"] for m in meals]

        plt.figure()
        plt.bar(meal_types, calories)
        plt.title("Calories per Meal")
        plt.xlabel("Meal")
        plt.ylabel("Calories")
        plt.tight_layout()
        plt.show()

    def visualize_macros(self, meals):
        """
        Pie chart of total macronutrient distribution.
        """
        total_protein = sum(m["macros"]["protein"] for m in meals)
        total_carbs = sum(m["macros"]["carbs"] for m in meals)
        total_fat = sum(m["macros"]["fat"] for m in meals)

        labels = ["Protein", "Carbs", "Fat"]
        sizes = [total_protein, total_carbs, total_fat]

        plt.figure()
        plt.pie(sizes, labels=labels, autopct="%1.1f%%")
        plt.title("Daily Macronutrient Distribution")
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    # Example usage
    viz = Visualizer()

    # Load logs
    daily_logs = viz.load_daily_log("data/daily_log.json")

    # Latest day and overall charts
    last_day = daily_logs[-1]
    print(f"Date: {last_day['date']}")

    # 1. Bar chart for the latest day
    viz.visualize_calories(last_day["meals"])

    # 2. Pie chart for the latest day
    viz.visualize_macros(last_day["meals"])

    # 3. Line chart for the period
    viz.visualize_daily_total_calories(daily_logs)
