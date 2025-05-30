import streamlit as st
import google.generativeai as genai
from datetime import datetime

# secrets.toml에서 API 키 불러오기
GOOGLE_API_KEY = st.secrets["general"]["GOOGLE_API_KEY"]

genai.configure(api_key=GOOGLE_API_KEY)

# 별자리 계산 함수
ZODIAC_DATES = [
    ((1, 20), (2, 18), "물병자리"),
    ((2, 19), (3, 20), "물고기자리"),
    ((3, 21), (4, 19), "양자리"),
    ((4, 20), (5, 20), "황소자리"),
    ((5, 21), (6, 21), "쌍둥이자리"),
    ((6, 22), (7, 22), "게자리"),
    ((7, 23), (8, 22), "사자자리"),
    ((8, 23), (9, 22), "처녀자리"),
    ((9, 23), (10, 22), "천칭자리"),
    ((10, 23), (11, 22), "전갈자리"),
    ((11, 23), (12, 21), "사수자리"),
    ((12, 22), (1, 19), "염소자리"),
]

def get_zodiac_sign(month: int, day: int) -> str:
    for start, end, sign in ZODIAC_DATES:
        start_month, start_day = start
        end_month, end_day = end
        if (month == start_month and day >= start_day) or (month == end_month and day <= end_day):
            return sign
        if start_month < end_month and start_month < month < end_month:
            return sign
        if start_month > end_month and (month > start_month or month < end_month):
            return sign
    return "알 수 없음"

# 세션 상태에 대화 저장 초기화
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# 타이틀 및 설명
st.title("AI 운세 챗봇 ✨")
st.write("원하는 방식으로 오늘의 운세를 확인해보세요!\n\n성격, 대인관계, 직업운까지 모두 알려드립니다.")

# 운세 보기 옵션 버튼
option = st.radio(
    "운세를 어떤 방식으로 볼까요?",
    ("별자리로 보기", "생년월일로 보기"),
    key="fortune_option"
)

zodiac = None
user_input = ""

if option == "별자리로 보기":
    zodiac = st.selectbox(
        "별자리를 선택하세요:",
        ["양자리", "황소자리", "쌍둥이자리", "게자리", "사자자리", "처녀자리", "천칭자리", "전갈자리", "사수자리", "염소자리", "물병자리", "물고기자리"],
        key="zodiac_select"
    )
    user_input = zodiac
elif option == "생년월일로 보기":
    birth = st.text_input("생년월일을 입력하세요 (YYYY-MM-DD):", key="birth_input")
    if birth:
        try:
            dt = datetime.strptime(birth, "%Y-%m-%d")
            zodiac = get_zodiac_sign(dt.month, dt.day)
            user_input = f"{birth} (계산된 별자리: {zodiac})"
        except ValueError:
            st.warning("생년월일 형식이 올바르지 않습니다. 예: 1990-05-21")

# Gemini API 호출 및 대화 누적
if st.button("운세 보기"):
    if not zodiac or zodiac == "알 수 없음":
        st.warning("별자리를 올바르게 선택하거나 생년월일을 정확히 입력해주세요.")
    else:
        prompt = f"""
        사용자의 별자리: {zodiac}
        오늘의 운세를 아래 3가지 항목으로 자세히 알려줘.
        1. 성격 및 심리적 경향
        2. 대인관계 및 인간관계 운
        3. 직업 및 일 관련 운
        각 항목별로 친근하고 긍정적으로 설명해줘.
        """
        st.session_state["messages"].append({
            "role": "user",
            "option": option,
            "content": user_input
        })
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)
            answer = response.text if hasattr(response, "text") else str(response)
            st.session_state["messages"].append({
                "role": "assistant",
                "option": option,
                "content": answer
            })
        except Exception as e:
            st.warning(f"Gemini API 호출 중 오류가 발생했습니다: {e}")

# 대화 내용 표시
st.subheader("대화 기록")
for msg in st.session_state["messages"]:
    st.markdown(f"**[{msg['role']}]** ({msg['option']}) : {msg['content']}")
