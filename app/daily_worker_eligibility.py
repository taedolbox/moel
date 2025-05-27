import streamlit as st
import pandas as pd
from datetime import datetime, date
import calendar
import pytz

# 달력 시작 요일 설정
calendar.setfirstweekday(calendar.SUNDAY)

# KST 시간대 설정
KST = pytz.timezone('Asia/Seoul')
current_datetime = datetime.now(KST)
current_time_korean = current_datetime.strftime('%Y년 %m월 %d일 %A 오후 %I:%M KST')

# 스타일시트 로드
with open("static/styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def render_calendar(apply_date):
    if 'selected_dates' not in st.session_state:
        st.session_state.selected_dates = set()

    selected_dates = st.session_state.selected_dates
    current_date = current_datetime.date()
    start_date = (apply_date.replace(day=1) - pd.DateOffset(months=1)).replace(day=1).date()
    months = sorted(set((d.year, d.month) for d in pd.date_range(start=start_date, end=apply_date)))

    with st.form(key="calendar_form"):
        for year, month in months:
            st.markdown(f"### {year}년 {month}월", unsafe_allow_html=True)
            cal = calendar.monthcalendar(year, month)
            days_of_week = ["일", "월", "화", "수", "목", "금", "토"]

            # 요일 헤더
            with st.container():
                cols = st.columns(7, gap="small")
                for i, day in enumerate(days_of_week):
                    with cols[i]:
                        class_name = "day-header"
                        if i == 0 or i == 6:
                            class_name += " weekend"
                        st.markdown(f'<div class="{class_name}">{day}</div>', unsafe_allow_html=True)

            # 날짜 렌더링
            for week in cal:
                with st.container():
                    cols = st.columns(7, gap="small")
                    for i, day in enumerate(week):
                        with cols[i]:
                            if day == 0:
                                st.empty()
                                continue
                            date_obj = date(year, month, day)
                            is_selected = date_obj in selected_dates
                            is_current = date_obj == current_date
                            is_disabled = date_obj > apply_date

                            class_name = "day"
                            if is_selected:
                                class_name += " selected"
                            if is_current:
                                class_name += " current"
                            if is_disabled:
                                class_name += " disabled"

                            with st.container():
                                if is_disabled:
                                    st.markdown(f'<div class="{class_name}">{day}</div>', unsafe_allow_html=True)
                                else:
                                    checkbox_key = f"date_{date_obj}"
                                    st.markdown(
                                        f'<div class="{class_name}" data-date="{date_obj}">{day}</div>',
                                        unsafe_allow_html=True
                                    )
                                    checkbox_value = st.checkbox(
                                        "", key=checkbox_key, value=is_selected, label_visibility="hidden"
                                    )
                                    if checkbox_value != is_selected:
                                        if checkbox_value:
                                            selected_dates.add(date_obj)
                                        else:
                                            selected_dates.discard(date_obj)
                                        st.session_state.selected_dates = selected_dates

        # 폼 제출 버튼 (렌더링 최적화)
        st.form_submit_button("선택 완료", on_click=lambda: None)

    # 선택된 근무일자 표시
    if selected_dates:
        st.markdown("### ✅ 선택된 근무일자")
        st.write(", ".join([d.strftime("%Y-%m-%d") for d in sorted(selected_dates)]))

    # 조건 표시
    total_days = 56
    threshold = total_days / 3  # 18.7일
    worked_days = len(selected_dates)
    condition_1 = worked_days < threshold
    condition_2 = True
    st.markdown("### 근로자 신청 가능 여부")
    st.markdown(f"**총 기간 일수**: {total_days}일")
    st.markdown(f"**기준 (1/3)**: {threshold:.1f}일")
    st.markdown(f"**근무일 수**: {worked_days}일")
    st.markdown(f"**조건 1**: {'충족 ✅' if condition_1 else '미충족 ❌'}")
    st.markdown(f"**조건 2**: 충족 ✅")
    st.markdown("### 최종 판단")
    st.markdown(f"**일반일용근로자**: {'신청 가능 ✅' if condition_1 else '신청 불가 ❌'}")
    st.markdown(f"**건설일용근로자**: {'신청 가능 ✅' if condition_1 else '신청 불가 ❌'}")

def daily_worker_eligibility_app():
    st.header("일용근로자 수급자격 요건 모의계산")
    st.markdown(f"**오늘 날짜와 시간**: {current_time_korean}")
    st.markdown("**안내**: 날짜의 좌측 영역(녹색 점)을 클릭해 선택하세요. 선택된 날짜는 빨간 테두리로 표시됩니다.")
    apply_date = st.date_input("수급자격 신청일을 선택하세요", value=current_datetime.date())
    render_calendar(apply_date)

if __name__ == "__main__":
    daily_worker_eligibility_app()
