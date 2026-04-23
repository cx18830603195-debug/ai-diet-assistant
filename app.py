import streamlit as st
import requests
from datetime import datetime
from mcp_tools import record_diet, get_calories

# ====================== 模型 ======================
API_URL = "http://localhost:11434/api/chat"
MODEL = "llama3.1:8b"

# ====================== 记忆 ======================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "diet_log" not in st.session_state:
    st.session_state.diet_log = []

# ====================== MCP 工具调用 ======================
def call_mcp(name, **kwargs):
    if name == "record":
        res = record_diet(**kwargs)
        st.session_state.diet_log.append({
            "time": datetime.now().strftime("%H:%M"),
            "type": kwargs["meal_type"],
            "food": kwargs["food"]
        })
        return res
    elif name == "calories":
        return get_calories(**kwargs)
    return ""

# ====================== 意图识别（不存问句） ======================
def run_tool(user_input):
    ui = user_input.strip()
    if "吃了" in ui and "?" not in ui:
        meal = None
        if "早上" in ui: meal = "早餐"
        elif "中午" in ui: meal = "午餐"
        elif "晚上" in ui: meal = "晚餐"
        food = ui.replace("我","").replace("吃了","").replace("早上","").replace("中午","").replace("晚上","").strip()
        if meal and food and food not in ["什么", "呢"]:
            return call_mcp("record", meal_type=meal, food=food)

    if "热量" in ui:
        food = ui.replace("热量","").replace("多少","").replace("?","").strip()
        if food:
            return call_mcp("calories", food=food)
    return None

# ====================== 大模型 ======================
def agent(prompt):
    history = "\n".join([f"{x['time']} | {x['type']}：{x['food']}" for x in st.session_state.diet_log])
    sys = f"""
你是专业饮食助手。
规则：
1. 用户问吃了什么，必须根据今日饮食记录回答。
2. 热量用真实数据，不编造。
3. 推荐家常菜：番茄炒蛋、鸡蛋羹、水煮蛋、鸡胸肉炒西兰花。
4. 自然、简洁、无错误。

今日饮食记录：
{history}
"""
    messages = [
        {"role": "system", "content": sys},
        *st.session_state.messages,
        {"role": "user", "content": prompt}
    ]
    try:
        r = requests.post(API_URL, json={"model": MODEL, "messages": messages, "stream": False})
        return r.json()["message"]["content"].strip()
    except:
        return "❌ 模型连接失败"

# ====================== 界面 ======================
st.set_page_config(page_title="饮食助手", layout="wide")
st.title("🍽️AI饮食助手")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("聊天、记录饮食、查热量")

if user_input:
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("assistant"):
        tool_msg = run_tool(user_input)
        reply = agent(user_input)
        if tool_msg:
            st.success(tool_msg)
        st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})

# ====================== 侧边栏 ======================
with st.sidebar:
    st.subheader("📝 饮食记录")
    for item in st.session_state.diet_log:
        st.write(f"🕒 {item['time']} | {item['type']}：{item['food']}")