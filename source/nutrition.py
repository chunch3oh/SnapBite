import gradio as gr

class NutritionAnalyzer:
    def get_user_info(self) -> tuple:
        """
        讀取使用者輸入的身高、體重與飲食目標。
        回傳: height (公分), weight (公斤), goal (字串)
        """
        try:
            height = float(input("請輸入你的身高 (公分): "))
            weight = float(input("請輸入你的體重 (公斤): "))
            goal = input("請輸入你的飲食目標 (減脂/維持/增肌): ")
        except ValueError:
            print("輸入有誤，請輸入數值。")
            exit(1)
        return height, weight, goal

    def calculate_bmi(self, weight: float, height: float) -> float:
        """
        計算 BMI = 體重(kg) / (身高(m))^2
        """
        return weight / ((height / 100) ** 2)

    def suggest_calories(self, weight: float, goal: str) -> float:
        """
        根據體重與目標計算建議每日熱量:
          - 減脂: 每公斤 25 大卡
          - 維持: 每公斤 30 大卡
          - 增肌: 每公斤 35 大卡
        """
        goal = goal.strip()
        if goal == "減脂":
            return weight * 25
        elif goal == "維持":
            return weight * 30
        elif goal == "增肌":
            return weight * 35
        else:
            raise ValueError("未知目標，請輸入「減脂」、「維持」或「增肌」。")


if __name__ == "__main__":
    # CLI 執行
    analyzer = NutritionAnalyzer()
    height, weight, goal = analyzer.get_user_info()
    bmi = analyzer.calculate_bmi(weight, height)
    calories = analyzer.suggest_calories(weight, goal)
    print(f"\n你的 BMI 為: {bmi:.2f}")
    print(f"依照「{goal}」目標，建議每日熱量攝取: {calories:.0f} 大卡")