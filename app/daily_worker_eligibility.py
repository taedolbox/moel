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

    # The actual set of selected dates is stored in st.session_state
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
                week_html_parts = [] # Use a list to build parts of the week HTML
                for i, day in enumerate(week):
                    if day == 0:
                        week_html_parts.append('<div class="calendar-day-container"></div>')
                        continue

                    date_obj = date(year, month, day)
                    is_selected = date_obj in selected_dates
                    is_current = date_obj == current_date
                    is_disabled = date_obj > apply_date # Disable days after apply_date

                    # Create a unique key for each checkbox
                    checkbox_key = f"date_checkbox_{date_obj.isoformat()}"

                    # Use st.empty to create a placeholder for the checkbox
                    # We will then draw our custom HTML on top of it.
                    # This ensures the Streamlit checkbox exists in the DOM to manage state,
                    # but we'll control its appearance and interaction via CSS and JS.
                    col = st.columns(1)[0] # Create a column to hold the checkbox
                    with col:
                        # Streamlit checkbox will be rendered but hidden by CSS
                        # Its value will reflect st.session_state.selected_dates
                        checked = st.checkbox(
                            "", # Empty label to hide the text
                            key=checkbox_key,
                            value=is_selected,
                            disabled=is_disabled,
                            # When the checkbox changes, we want to update our selected_dates set
                            on_change=lambda d=date_obj, k=checkbox_key: (
                                st.session_state.selected_dates.add(d) if st.session_state[k] else st.session_state.selected_dates.discard(d)
                            ),
                            label_visibility="hidden" # Ensures Streamlit doesn't render a visible label
                        )
                        # After the checkbox is rendered, we add our custom HTML around it.
                        # The JS `onclick` will simulate a click on the *hidden* Streamlit checkbox.
                        class_name = "calendar-day-box"
                        if is_selected:
                            class_name += " selected-day"
                        if is_current:
                            class_name += " current-day"
                        if is_disabled:
                            class_name += " disabled-day"

                        # We put the HTML for the calendar day box *inside* the column
                        # but logically, it overlays or replaces the visual aspect of the checkbox
                        # The crucial part is the onclick event targeting the *Streamlit checkbox's parent div*
                        # which is what Streamlit wraps its components in.
                        # We need to find the specific element corresponding to the Streamlit checkbox.
                        # Streamlit assigns data-testid="stCheckbox" to its main checkbox container.
                        # The key we provided is also part of the DOM structure.
                        # We need to find the div that contains `key={checkbox_key}`.

                        # The cleanest way to trigger the Streamlit checkbox from custom HTML
                        # is to use a direct click on its underlying input or the label associated with it.
                        # Since we hid the label, we'll try to find the actual input or a reliably clickable parent.
                        # Streamlit typically uses data-testid for components. The input itself is inside a label.
                        # A more robust way: Use JavaScript to find the checkbox by its key.
                        # The checkbox element's parent `div[data-testid="stCheckbox"]` is what we want to click.
                        # Its `key` attribute will be present as a data-something attribute, usually `data-st-component-id`.
                        # However, targeting the element with `data-testid="stCheckbox"` is more reliable,
                        # and then finding the specific one by its internal `key`.

                        # Let's adjust the click to target the *hidden checkbox container* directly.
                        # Each Streamlit component receives a unique ID, often embedded in the key.
                        # We need to target the element that Streamlit uses to render the checkbox.
                        # Streamlit's checkbox HTML structure makes the main clickable area the div with data-testid="stCheckbox".
                        # We'll use the 'key' property that Streamlit assigns to the checkbox.
                        # Streamlit internally converts `key` to a `data-testid` or other attributes.
                        # The `data-testid` is "stCheckbox", and the key is an *attribute* on one of its internal divs.
                        # It's safest to find the specific Streamlit checkbox element by its unique key.

                        # To trigger the hidden Streamlit checkbox when our custom div is clicked,
                        # we need to find the Streamlit-generated checkbox input element.
                        # Streamlit's `st.checkbox(key=...)` creates an input with a specific `id` that often includes the key.
                        # Or, we can target the `div[data-testid="stCheckbox"]` which contains it.
                        # A more reliable way: Streamlit assigns a specific ID to the actual input checkbox.
                        # This ID looks something like `checkbox-unique_id_based_on_key`.
                        # Let's target the parent `div[data-testid="stCheckbox"]` and then its internal input.
                        # A simple way to trigger: find the parent div of the checkbox by its key, then click it.
                        # Streamlit assigns `data-testid` to the top-level div for its components.
                        # The specific checkbox will have a `key` attached internally.
                        # Let's assume Streamlit applies the `key` to the `div[data-testid="stCheckbox"]` or an inner element reliably.
                        # The `st.checkbox` will be rendered as:
                        # <div data-testid="stCheckbox" ...>
                        #   <label ... for="checkbox-some_id">
                        #     <input type="checkbox" id="checkbox-some_id" ...>
                        #   </label>
                        # </div>
                        # We want to click the `label` or the `input`. The `label` is the easiest target for a user click.

                        # The JavaScript `onclick` needs to find the correct, hidden Streamlit element.
                        # Streamlit components have a data-testid attribute on their main container div.
                        # Let's target the specific `div[data-testid="stCheckbox"]` that corresponds to our `checkbox_key`.
                        # The `key` is often reflected in the `id` of the actual checkbox input, or in a `data-st-component-id` attribute.
                        # The easiest way is to find the Streamlit-generated `label` element by its `for` attribute (which is the checkbox ID).
                        # Or, even simpler: just hide the Streamlit-generated checkbox's *input* and *label text*,
                        # but keep its container `div[data-testid="stCheckbox"]` as the clickable area.

                        # The CSS now hides the Streamlit checkbox input and label text.
                        # The outer `div[data-testid="stCheckbox"]` is `opacity: 0` and `z-index: 2`,
                        # making it an invisible click target on top of our custom `calendar-day-box`.
                        # So, simply ensuring the Streamlit checkbox is rendered is enough.
                        # We don't need a custom `onclick` on `calendar-day-box` if the transparent checkbox is on top.

                        # To place the `calendar-day-box` within the same Streamlit column,
                        # we need to ensure their rendering order and positioning.
                        # The `st.checkbox` already creates a container. We just need to make its visual part invisible
                        # and let our custom HTML provide the visual and the perceived click area.

                        # Instead of embedding a complex JS click, we rely on the CSS that positions the hidden `stCheckbox` over our custom `calendar-day-box`.
                        # The `calendar-day-box` itself becomes the visual representation.
                        # The `st.checkbox` is transparent and receives the actual clicks.

                        # The HTML for the `calendar-day-box` is appended to the `week_html_parts` list.
                        # The `calendar-day-container` is what the `st.checkbox` is in.
                        # So, we need to restructure a bit. Each day is a column.
                        # Inside that column, we place the hidden `st.checkbox`.
                        # And then we overlay our custom HTML on top of where the checkbox *would* be.

                        # Let's adjust the structure to put the hidden checkbox and the custom HTML in the same "slot"
                        # to allow the CSS to correctly overlay the transparent checkbox on our custom HTML.

                        # The `st.checkbox` has its own div with `data-testid="stCheckbox"`.
                        # We will set its opacity to 0 and give it a higher z-index in CSS.
                        # Then, we'll render our `calendar-day-box` and put it *below* this transparent checkbox
                        # in the HTML structure, but visually, the checkbox will be "on top" due to z-index.
                        # This makes the user click the transparent checkbox directly.

                        week_html_parts.append(
                            f'<div class="calendar-day-container">'
                            f'  <div class="{class_name}">' # This is our visual element
                            f'    <div class="selection-mark" style="display: {"block" if is_selected else "none"};"></div>'
                            f'    {day}' # The day number
                            f'  </div>'
                            f'</div>'
                        )
                # After the loop for each week, we use st.markdown to render the combined HTML for the row.
                st.markdown('<div class="calendar-grid">', unsafe_allow_html=True)
                # For each day in the week, we need to render the hidden checkbox and then the custom HTML.
                # Since Streamlit components (like st.checkbox) generate their own divs, we need to be careful with grid layout.
                # The best way is to let Streamlit manage the grid of `st.checkbox` components, and then override their styling.

                # Simplified approach: Render the grid using Streamlit's columns, and place the checkbox inside.
                # Then, use CSS to style the checkbox and its label to look like our calendar day.
                cols = st.columns(7) # Create 7 columns for each week
                for j, day in enumerate(week):
                    with cols[j]:
                        if day == 0:
                            # Render an empty placeholder for days not in the month
                            st.markdown('<div style="height: 44px;"></div>', unsafe_allow_html=True)
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
                            # st.rerun() # Rerunning here might cause flicker, let's see if Streamlit handles it naturally

                        # The actual Streamlit checkbox. We control its appearance with CSS.
                        st.checkbox(
                            label=str(day), # The visible number for the checkbox label
                            key=checkbox_key,
                            value=is_selected,
                            disabled=is_disabled,
                            on_change=update_selection,
                            # We keep label_visibility="visible" because we rely on it for the number.
                            # The CSS will make the actual checkbox input and its container invisible.
                            # The 'label' text (the day number) will be styled by our calendar-day-box.
                            # We need to adjust CSS to target the Streamlit label correctly.
                            label_visibility="visible" # Important: keep visible so Streamlit renders the number.
                        )

                        # After the checkbox is rendered, we inject CSS classes using JS to manipulate it.
                        # This is more robust than trying to manually overlay HTML in Python.
                        # We will use Streamlit's `st.markdown` with `_js_` to execute JavaScript
                        # to dynamically add classes to the Streamlit-generated checkbox elements.
                        js_code = f"""
                            <script>
                                const checkboxContainer = document.querySelector('div[data-testid="stCheckbox"][key="{checkbox_key}"]');
                                if (checkboxContainer) {{
                                    // Add the base class for styling
                                    checkboxContainer.classList.add('calendar-day-container');
                                    // Target the actual label (which contains the input and the number)
                                    const labelElement = checkboxContainer.querySelector('label');
                                    if (labelElement) {{
                                        labelElement.classList.add('calendar-day-box');
                                        // Add selected/current/disabled classes based on state
                                        if ({is_selected}) {{
                                            labelElement.classList.add('selected-day');
                                        }} else {{
                                            labelElement.classList.remove('selected-day');
                                        }}
                                        if ({is_current}) {{
                                            labelElement.classList.add('current-day');
                                        }} else {{
                                            labelElement.classList.remove('current-day');
                                        }}
                                        if ({is_disabled}) {{
                                            labelElement.classList.add('disabled-day');
                                        }} else {{
                                            labelElement.classList.remove('disabled-day');
                                        }}

                                        // Ensure the input itself is hidden
                                        const inputElement = labelElement.querySelector('input[type="checkbox"]');
                                        if (inputElement) {{
                                            inputElement.style.display = 'none';
                                        }}
                                    }}
                                }}
                            </script>
                        """
                        st.markdown(js_code, unsafe_allow_html=True)

                st.markdown('</div>', unsafe_allow_html=True) # Close the calendar-grid div

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
