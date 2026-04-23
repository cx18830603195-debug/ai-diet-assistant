from mcp.server import FastMCP
from pydantic import BaseModel

# ====================== MCP 服务启动 ======================
mcp = FastMCP("饮食助手工具")

# ====================== 工具 1：记录饮食 ======================
class DietRecord(BaseModel):
    meal_type: str
    food: str

@mcp.tool()
def record_diet(meal_type: str, food: str) -> str:
    """
    记录用户的饮食（早餐/午餐/晚餐）
    """
    return f"✅ [MCP] 已记录 {meal_type}：{food}"

# ====================== 工具 2：查询食物热量 ======================
@mcp.tool()
def get_calories(food: str) -> str:
    """
    查询常见食物的真实热量
    """
    data = {
        "鸡蛋": "1个中等鸡蛋 ≈ 70大卡",
        "煮鸡蛋": "1个煮鸡蛋 ≈ 70大卡",
        "煎蛋": "1个煎蛋 ≈ 90大卡",
        "鸡胸肉": "100g ≈ 165大卡",
        "米饭": "100g熟米饭 ≈ 116大卡",
        "牛奶": "250ml牛奶 ≈ 150大卡",
        "汉堡": "1个汉堡 ≈ 250~400大卡"
    }
    return data.get(food, f"{food} 约 120~300大卡/100g")

# ====================== 运行 MCP 服务 ======================
if __name__ == "__main__":
    mcp.run()