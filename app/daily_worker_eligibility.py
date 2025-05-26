import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
import calendar

# Set the first day of the week to Sunday
calendar.setfirstweekday(calendar.SUNDAY)

# Current date and time (May 26, 2025, 3:36 PM KST)
current_datetime = datetime(2025, 5, 26, 15, 36)

def get_date_range(apply_date):
    """Returns the date range from the beginning of the previous month to the apply_date."""
    start_date = (apply_date.replace(day=1) - pd.DateOffset(months=1)).replace(day=1).date()
    return [d.date() for d in pd.date_range(start=start_date, end=apply_date)]

def render_calendar_interactive(apply_date):
    """Renders the calendar with selectable dates."""
    # Initialize session state for selected_dates if it doesn't exist
    if 'selected_dates' not in st.session_state:
        st.session_state.selected_dates = set()

    selected_dates = st.session_state.selected_dates
    current_date = current_datetime.date()

    # Calculate month range to display in the calendar
    start_date_for_calendar = (apply_date.replace(day=1) - pd.DateOffset(months=1)).replace(day=1).date()
    end_date_for_calendar = apply_date
    months_to_display = sorted(list(set((d.year, d.month) for d in pd.date_range(start=start_date_for_calendar, end=end_date_for_calendar))))

    # Calendar container
    with st.container():
        st.markdown('<div class="calendar-wrapper">', unsafe_allow_html=True)
        for year, month in months_to_display:
            cal = calendar.monthcalendar(year, month)

            # Render calendar days
            for week in cal:
                cols = st.columns(7, gap="small")
                for i, day in enumerate(week):
                    with cols[i]:
                        if day == 0:
                            st.markdown('<div class="calendar-day-container"></div>', unsafe_allow_html=True)
                            continue
                        date_obj = date(year, month, day)

                        # Disable dates after the apply_date
                        if date_obj > apply_date:
                            st.markdown(
                                f'<div class="calendar-day-container">'
                                f'<div class="calendar-day-box disabled-day">{day}</div>'
                                f'</div>',
                                unsafe_allow_html=True
                            )
                            continue

                        is_selected = date_obj in selected_dates
                        is_current = date_obj == current_date
                        class_name = "calendar-day-box"

                        if is_selected:
                            class_name += " selected-day"
                        if is_current:
                            class_name += " current-day"

                        # Create a clickable button for each day
                        if st.button(str(day), key=f"day_{year}_{month}_{day}", use_container_width=True):
                            if date_obj in selected_dates:
                                selected_dates.remove(date_obj)
                            else:
                                selected_dates.add(date_obj)
                            st.session_state.selected_dates = selected_dates # Update session state
                            st.experimental_rerun() # Rerun to update calendar display
                        
                        # Apply CSS classes to the button
                        st.markdown(
                            f"""
                            <style>
                                div[data-testid="column"] > button[key="day_{year}_{month}_{day}"] {{
                                    background-color: {'#4CAF50' if is_selected else '#f0f2f6'};
                                    color: {'white' if is_selected else 'black'};
                                    border-radius: 5px;
                                    border: 1px solid {'#4CAF50' if is_selected else '#ccc'};
                                    padding: 10px 0;
                                    text-align: center;
                                    text-decoration: none;
                                    display: inline-block;
                                    font-size: 16px;
                                    margin: 2px;
                                    cursor: pointer;
                                }}
                                div[data-testid="column"] > button[key="day_{year}_{month}_{day}"]:hover {{
                                    background-color: {'#45a049' if is_selected else '#e0e0e0'};
                                }}
                                {'div[data-testid="column"] > button[key="day_' + str(year) + '_' + str(month) + '_' + str(day) + '"] { border: 2px solid blue; }' if is_current else ''}
                            </style>
                            """,
                            unsafe_allow_html=True
                        )
        st.markdown('</div>', unsafe_allow_html=True)

    # Display currently selected work dates
    if st.session_state.selected_dates:
        st.markdown("### ✅ 선택된 근무일자")
        st.markdown(", ".join([d.strftime("%Y-%m-%d") for d in sorted(st.session_state.selected_dates)]))

    return st.session_state.selected_dates

def daily_worker_eligibility_app():
    """Main function for the daily worker eligibility simulation app."""
    st.header("일용근로자 수급자격 요건 모의계산")

    # Select application date
    apply_date = st.date_input("수급자격 신청일을 선택하세요", value=current_datetime.date(), key="apply_date_input")

    st.markdown("---")
    st.markdown("#### ✅ 근무일 선택 달력")
    render_calendar_interactive(apply_date)
    st.markdown("---")

if __name__ == "__main__":
    daily_worker_eligibility_app()
