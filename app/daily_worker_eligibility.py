import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
import calendar

# 달력의 시작 요일을 일요일로 설정
calendar.setfirstweekday(calendar.SUNDAY)

# 현재 날짜와 시간 (2025년 5월 27일 오후 6:19 KST)
current_datetime = datetime(2025, 5, 27, 18, 19)
current_time_korean = current_datetime.strftime('%Y년 %m월 %d일 %A 오후 %I:%M KST')

def get_date_range(apply_date):
    """신청일을 기준으로 이전 달 초일부터 신청일까지의 날짜 범위를 반환합니다."""
    start_date = (apply_date.replace(day=1) - pd.DateOffset(months=1)).replace(day=1).date()
    return [d.date() for d in pd.date_range(start=start_date, end=apply_date)], start_date

def render_calendar_interactive(apply_date):
    """달력을 렌더링하고 날짜 선택 기능을 제공합니다. CSS는 styles.css에서 로드됩니다."""
    # 초기 세션 상태 설정
    if 'selected_dates' not in st.session_state:
        st.session_state.selected_dates = set()

    selected_dates = st.session_state.selected_dates
    current_date = current_datetime.date()

    # 달력 표시할 월 범위 계산
    start_date_for_calendar = (apply_date.replace(day=1) - pd.DateOffset(months=1)).replace(day=1).date()
    end_date_for_calendar = apply_date
    months_to_display = sorted(list(set((d.year, d.month) for d in pd.date_range(start=start_date_for_calendar, end=end_date_for_calendar))))

    # 달력 전용 컨테이너
    with st.container():
        st.markdown('<div class="calendar-wrapper">', unsafe_allow_html=True)
        for year, month in months_to_display:
            st.markdown(f"<h3>{year}년 {month}월</h3>", unsafe_allow_html=True)
            cal = calendar.monthcalendar(year, month)
            days_of_week_korean = ["일", "월", "화", "수", "목", "금", "토"]

            # 요일 헤더 생성 (7열 고정)
            header_html = '<div class="header-grid">'
            for i, day_name in enumerate(days_of_week_korean):
                color = "red" if i == 0 or i == 6 else "#000000"
                header_html += f'<div class="day-header"><span style="color: {color}">{day_name}</span></div>'
            header_html += '</div>'
            st.markdown(header_html, unsafe_allow_html=True)

            # 달력 렌더링
            for week in cal:
                cols = st.columns(7) # Create 7 columns for each week
                for j, day in enumerate(week):
                    with cols[j]:
                        if day == 0:
                            # Empty slot for days not in the month
                            st.markdown('<div class="calendar-day-container"></div>', unsafe_allow_html=True)
                            continue

                        date_obj = date(year, month, day)
                        is_selected = date_obj in selected_dates
                        is_current = date_obj == current_date
                        is_disabled = date_obj > apply_date

                        checkbox_key = f"date_checkbox_{date_obj.isoformat()}"

                        # Conditional logic for on_change: if the checkbox is checked, add to set; if unchecked, remove from set.
                        # Using a lambda with default arguments to capture `date_obj` and `checkbox_key` for each iteration.
                        def update_selection(d_obj=date_obj, k_key=checkbox_key):
                            if st.session_state[k_key]:
                                st.session_state.selected_dates.add(d_obj)
                            else:
                                st.session_state.selected_dates.discard(d_obj)
                            # Streamlit will automatically rerun and re-render the components with updated state.

                        # The actual Streamlit checkbox.
                        # The `label` will be the day number.
                        # Its appearance will be completely controlled by CSS.
                        st.checkbox(
                            label=str(day), # The visible number for the checkbox label
                            key=checkbox_key,
                            value=is_selected,
                            disabled=is_disabled,
                            on_change=update_selection,
                            label_visibility="visible" # Keep visible so Streamlit renders the number inside the label
                        )

                        # Inject custom data attributes into the label for CSS targeting
                        # Streamlit assigns `data-testid="stCheckbox"` to the outer div.
                        # The actual label (which contains the number) is inside.
                        # We need to find the `label` element associated with our checkbox and add attributes to it.
                        # Using a unique ID for the label or using its association with the checkbox input's ID.
                        # A more robust way to target the label: Streamlit usually generates an ID for the input, and the label's `for` attribute points to it.
                        # We can inject a script to find the label element and add custom attributes.

                        # The Streamlit-generated label itself will be styled by our CSS.
                        # To pass custom state (selected, current, disabled) to CSS, we'll use data attributes.
                        # Since `st.checkbox` directly renders the label, we can't directly add data attributes in Python.
                        # We have to rely on CSS selecting based on the checkbox's checked state and then styling its label,
                        # OR use JS injection to add data attributes after rendering.
                        # Given Streamlit's rendering cycle, the latter is often more stable for fine-grained control.

                        # Let's add JavaScript to add custom data attributes to the label of the checkbox
                        # so that our CSS can pick up the `selected-day`, `current-day`, `disabled-day` states.
                        js_for_styling = f"""
                            <script>
                                // Find the specific checkbox container by its data-testid and key
                                const checkboxContainer = document.querySelector('div[data-testid="stCheckbox"][key="{checkbox_key}"]');
                                if (checkboxContainer) {{
                                    const labelElement = checkboxContainer.querySelector('label');
                                    if (labelElement) {{
                                        // Set data attributes for CSS targeting
                                        labelElement.setAttribute('data-selected-day', {str(is_selected).lower()});
                                        labelElement.setAttribute('data-current-day', {str(is_current).lower()});
                                        labelElement.setAttribute('data-disabled-day', {str(is_disabled).lower()});

                                        // Ensure the input element is completely hidden within the label
                                        const inputElement = labelElement.querySelector('input[type="checkbox"]');
                                        if (inputElement) {{
                                            inputElement.style.display = 'none';
                                        }}

                                        // Manually add the selection mark if it's selected
                                        if ({is_selected}) {{
                                            let selectionMark = labelElement.querySelector('.selection-mark');
                                            if (!selectionMark) {{
                                                selectionMark = document.createElement('div');
                                                selectionMark.className = 'selection-mark';
                                                labelElement.prepend(selectionMark); // Add at the beginning
                                            }}
                                            selectionMark.style.display = 'block';
                                        }} else {{
                                            let selectionMark = labelElement.querySelector('.selection-mark');
                                            if (selectionMark) {{
                                                selectionMark.style.display = 'none';
                                            }}
                                        }}
                                    }}
                                }}
                            </script>
                        """
                        st.markdown(js_for_styling, unsafe_allow_html=True)
                        # We don't need a separate `calendar-day-box` div because the checkbox label itself is styled to be the box.

                # No need for st.markdown('<div class="calendar-grid">') wrapping weeks, as st.columns handles the grid.
                # The .calendar-grid CSS class is now applied to the parent of the columns if needed for sizing.
                # However, for 7 columns, Streamlit's default behavior with `st.columns(7)` handles the grid.
                # We'll remove the explicit `<div class="calendar-grid">` from the Python side to avoid nesting issues.

        st.markdown('</div>', unsafe_allow_html=True) # Close calendar-wrapper

    # 선택된 근무일자 표시
    if st.session_state.selected_dates:
        st.markdown("### ✅ 선택된 근무일자")
        st.markdown(", ".join([d.strftime("%Y-%m-%d") for d in sorted(st.session_state.selected_dates)]))

    # 디버깅 정보 출력 (페이지 하단)
    st.markdown("### 🔍 디버깅 정보")
    st.write("**현재 세션 상태 (st.session_state):**")
    st.write(st.session_state)
    st.write("**선택된 날짜 (st.session_state.selected_dates):**")
    st.write([d.strftime("%Y-%m-%d") for d in sorted(st.session_state.selected_dates)])

    return st.session_state.selected_dates

def daily_worker_eligibility_app():
    """일용근로자 수급자격 요건 모의계산 앱의 메인 함수입니다."""
    st.header("일용근로자 수급자격 요건 모의계산")

    # 현재 날짜와 시간 표시
    st.markdown(f"**오늘 날짜와 시간**: {current_time_korean}", unsafe_allow_html=True)

    # 요건 조건 설명
    st.markdown("### 📋 요건 조건")
    st.markdown("- **조건 1**: 수급자격 인정신청일이 속한 달의 직전 달 초일부터 수급자격 인정신청일까지의 근로일 수가 총 일수의 1/3 미만이어야 합니다.")
    st.markdown("- **조건 2 (건설일용근로자만 해당)**: 수급자격 인정신청일 직전 14일간 근무 사실이 없어야 합니다 (신청일 제외).")
    st.markdown("---")

    # 수급자격 신청일 선택
    apply_date = st.date_input("수급자격 신청일을 선택하세요", value=current_datetime.date(), key="apply_date_input")

    # 날짜 범위 및 시작일 가져오기
    date_range_objects, start_date = get_date_range(apply_date)

    st.markdown("---")
    st.markdown("#### ✅ 근무일 선택 달력")
    selected_dates = render_calendar_interactive(apply_date)
    st.markdown("---")

    # 조건 1 계산 및 표시
    total_days = len(date_range_objects)
    worked_days = len(selected_dates)
    threshold = total_days / 3

    st.markdown(f"- 총 기간 일수: **{total_days}일**")
    st.markdown(f"- 기준 (총일수의 1/3): **{threshold:.1f}일**")
    st.markdown(f"- 선택한 근무일 수: **{worked_days}일**")

    condition1 = worked_days < threshold
    st.markdown(
        f'<div class="result-text">'
        f'<p>{"✅ 조건 1 충족: 근무일 수가 기준 미만입니다." if condition1 else "❌ 조건 1 불충족: 근무일 수가 기준 이상입니다."}</p>'
        f'</div>',
        unsafe_allow_html=True
    )

    # 조건 2 계산 및 표시 (건설일용근로자 기준)
    fourteen_days_prior_end = apply_date - timedelta(days=1)
    fourteen_days_prior_start = fourteen_days_prior_end - timedelta(days=13)
    fourteen_days_prior_range = [d.date() for d in pd.date_range(start=fourteen_days_prior_start, end=fourteen_days_prior_end)]
    no_work_14_days = all(day not in selected_dates for day in fourteen_days_prior_range)
    condition2 = no_work_14_days

    st.markdown(
        f'<div class="result-text">'
        f'<p>{"✅ 조건 2 충족: 신청일 직전 14일간(" + fourteen_days_prior_start.strftime("%Y-%m-%d") + " ~ " + fourteen_days_prior_end.strftime("%Y-%m-%d") + ") 근무내역이 없습니다." if no_work_14_days else "❌ 조건 2 불충족: 신청일 직전 14일간(" + fourteen_days_prior_start.strftime("%Y-%m-%d") + " ~ " + fourteen_days_prior_end.strftime("%Y-%m-%d") + ") 내 근무기록이 존재합니다."}</p>'
        f'</div>',
        unsafe_allow_html=True
    )

    st.markdown("---")

    # 조건 1 불충족 시 미래 신청일 제안
    if not condition1:
        st.markdown("### 📅 조건 1을 충족하려면 언제 신청해야 할까요?")
        found_suggestion = False
        for i in range(1, 31):
            future_date = apply_date + timedelta(days=i)
            date_range_future_objects, _ = get_date_range(future_date)
            total_days_future = len(date_range_future_objects)
            threshold_future = total_days_future / 3
            worked_days_future = sum(1 for d in selected_dates if d <= future_date)

            if worked_days_future < threshold_future:
                st.markdown(
                    f'<div class="result-text">'
                    f'<p>✅ <b>{future_date.strftime("%Y-%m-%d")}</b> 이후에 신청하면 요건을 충족할 수 있습니다.</p>'
                    f'</div>',
                    unsafe_allow_html=True
                )
                found_suggestion = True
                break
        if not found_suggestion:
            st.markdown(
                f'<div class="result-text">'
                f'<p>❗ 앞으로 30일 이내에는 요건을 충족할 수 없습니다. 근무일 수를 조정하거나 더 먼 날짜를 고려하세요.</p>'
                f'</div>',
                unsafe_allow_html=True
            )

    # 조건 2 불충족 시 미래 신청일 제안 (건설일용근로자 기준)
    if not condition2:
        st.markdown("### 📅 조건 2를 충족하려면 언제 신청해야 할까요?")
        last_worked_day = max((d for d in selected_dates if d < apply_date), default=None)
        if last_worked_day:
            suggested_date = last_worked_day + timedelta(days=15)
            st.markdown(
                f'<div class="result-text">'
                f'<p>✅ <b>{suggested_date.strftime("%Y-%m-%d")}</b> 이후에 신청하면 조건 2를 충족할 수 있습니다.</p>'
                f'</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f'<div class="result-text">'
                f'<p>이미 최근 14일간 근무내역이 없으므로, 신청일을 조정할 필요는 없습니다.</p>'
                f'</div>',
                unsafe_allow_html=True
            )

    st.subheader("📌 최종 판단")
    # 일반일용근로자: 조건 1만 판단
    if condition1:
        st.markdown(
            f'<div class="result-text">'
            f'<p>✅ 일반일용근로자: 신청 가능<br>'
            f'<b>수급자격 인정신청일이 속한 달의 직전 달 초일부터 수급자격 인정신청일까지({start_date.strftime("%Y-%m-%d")} ~ {apply_date.strftime("%Y-%m-%d")}) 근로일 수의 합이 같은 기간 동안의 총 일수의 3분의 1 미만</b></p>'
            f'</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f'<div class="result-text">'
            f'<p>❌ 일반일용근로자: 신청 불가능<br>'
            f'<b>수급자격 인정신청일이 속한 달의 직전 달 초일부터 수급자격 인정신청일까지({start_date.strftime("%Y-%m-%d")} ~ {apply_date.strftime("%Y-%m-%d")}) 근로일 수의 합이 같은 기간 동안의 총 일수의 3분의 1 이상입니다.</b></p>'
            f'</div>',
            unsafe_allow_html=True
        )

    # 건설일용근로자: 조건 1과 조건 2 모두 판단
    if condition1 and condition2:
        st.markdown(
            f'<div class="result-text">'
            f'<p>✅ 건설일용근로자: 신청 가능<br>'
            f'<b>수급자격 인정신청일이 속한 달의 직전 달 초일부터 수급자격 인정신청일까지({start_date.strftime("%Y-%m-%d")} ~ {apply_date.strftime("%Y-%m-%d")}) 근로일 수의 합이 총 일수의 3분의 1 미만이고, 신청일 직전 14일간({fourteen_days_prior_start.strftime("%Y-%m-%d")} ~ {fourteen_days_prior_end.strftime("%Y-%m-%d")}) 근무 사실이 없음을 확인합니다.</b></p>'
            f'</div>',
            unsafe_allow_html=True
        )
    else:
        error_message = "❌ 건설일용근로자: 신청 불가능<br>"
        if not condition1:
            error_message += f"<b>수급자격 인정신청일이 속한 달의 직전 달 초일부터 수급자격 인정신청일까지({start_date.strftime('%Y-%m-%d')} ~ {apply_date.strftime('%Y-%m-%d')}) 근로일 수의 합이 같은 기간 동안의 총 일수의 3분의 1 이상입니다.</b><br>"
        if not condition2:
            error_message += f"<b>신청일 직전 14일간({fourteen_days_prior_start.strftime('%Y-%m-%d')} ~ {fourteen_days_prior_end.strftime('%Y-%m-%d')}) 근무내역이 있습니다.</b>"
        st.markdown(
            f'<div class="result-text">'
            f'<p>{error_message}</p>'
            f'</div>',
            unsafe_allow_html=True
        )

if __name__ == "__main__":
    daily_worker_eligibility_app()
