import streamlit as st
from streamlit_calendar import calendar
from datetime import datetime

st.set_page_config(page_title="일용근로자 수급자격 모의계산기", layout="wide")
st.title("🗓️ 일용근로자 수급자격 모의계산기")

# 선택된 날짜 저장용 세션 상태 초기화
if "selected_dates" not in st.session_state:
    st.session_state.selected_dates = set()

st.markdown("### 🔽 수급자격 신청일 입력")
today = st.date_input("수급자격 신청일", value=datetime.today())

# 기준 기간 계산 (18개월 전부터 ~ 신청일 기준)
start_period = (today.replace(day=1) - pd.DateOffset(months=17)).date()
end_period = today

st.markdown(f"**기준 기간:** `{start_period}` ~ `{end_period}`")

st.markdown("---")
st.markdown("### 📅 아래 달력에서 근무일자를 선택하세요")

# 캘린더 렌더링
event = calendar()

# 날짜 클릭 이벤트 처리
if event and "start" in event:
    clicked_date = event["start"][:10]  # 'YYYY-MM-DD'
    if clicked_date in st.session_state.selected_dates:
        st.session_state.selected_dates.remove(clicked_date)
    else:
        st.session_state.selected_dates.add(clicked_date)

# 선택된 날짜 정렬
selected_list = sorted(st.session_state.selected_dates)

# 결과 표시
st.markdown("### ✅ 선택한 근무일")
if selected_list:
    for date in selected_list:
        st.markdown(f"- {date}")
    st.success(f"총 **{len(selected_list)}일** 선택됨")
else:
    st.warning("선택된 날짜가 없습니다.")
