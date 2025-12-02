from typing import Any, List


def _extract_items(analysis: Any) -> List[Any]:
    if hasattr(analysis, "food_items"):
        return getattr(analysis, "food_items")
    if isinstance(analysis, dict):
        return analysis.get("food_items", []) or []
    return []


def format_analysis_message(analysis: Any) -> str:
    items = _extract_items(analysis)
    if not items:
        return "未能解析圖片中的餐點，請再試一次或換張更清晰的照片。"

    lines = ["分析完成，營養摘要："]
    for item in items:
        name = getattr(item, "name", None) or item.get("name", "")
        portion = getattr(item, "portion_size", None) or item.get("portion_size", "")
        calories = getattr(item, "calories", None) or item.get("calories", "")
        macros_obj = getattr(item, "macronutrients", None) or item.get("macronutrients", {})
        carbs = getattr(macros_obj, "carbs", None) or macros_obj.get("carbs", "")
        protein = getattr(macros_obj, "protein", None) or macros_obj.get("protein", "")
        fat = getattr(macros_obj, "fat", None) or macros_obj.get("fat", "")

        lines.append(f"- {name}（{portion}）：{calories}，碳水 {carbs}、蛋白質 {protein}、脂肪 {fat}")

    lines.append("\n想再分析其他餐點，直接再傳一張照片即可。")
    return "\n".join(lines)

