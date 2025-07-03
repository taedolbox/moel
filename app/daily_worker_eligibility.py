import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import pytz
import pdfkit
import sqlite3
from jinja2 import Template
import smtplib
from email.message import EmailMessage

# ✅ 필수: set_page_config 최상단!
st.set_page_config(page_title="일용근로자 수급자격 모의계산", page_icon="✅")

KST = pytz.timezone('Asia/Seoul')

# ✅ DB 연결
conn = sqlite3.connect('eligibility_log.db', check_same_thread=False)
c = conn.cursor()
c.execute('''
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        apply_date TEXT,
        worked_days INTEGER,
        total_days INTEGER,
        cond1 INTEGER,
        cond2 INTEGER,
        email TEXT
    )
''')
conn.commit()

APP_VERSION = "v1.0.0"

def get_date_range(apply_date):
    start_of_apply_month = apply_date.replace(day=1)
    start_date = (start_of_apply_month - pd.DateOffset(months=1)).replace(day=1).date()
    return [d.date() for d in pd.date_range(start=start_date, end=apply_date)], start_date

def render_pdf(result_text):
    # HTML 템플릿
    html_template = Template("""
    <html><body>
    <h2>일용근로자 수급자격 모의계산 결과</h2>
    <pre>{{ result }}</pre>
    </body></html>
    """)
    html_out = html_template.render(result=result_text)
    pdf = pdfkit.from_string(html_out, False)
    return pdf

def send_email(receiver_email, result_text):
    sender_email = "your_email@example.com"
    sender_password = "your_password"
    msg = EmailMessage()
    msg['Subject'] = '일용근로자 수급자격 모의계산 결과'
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg.set_content(result_text)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(sender_email, sender_password)
        smtp.send_message(msg)

def daily_worker_eligibility_app():
    st.title(f"📌 일용근로자 수급자격 요건 모의계산 ({APP_VERSION})")

    current_datetime = datetime.now(KST)
    st.caption(f"**오늘:** {current_datetime.strftime('%Y-%m-%d %A %H:%M')}")

    st.markdown("""
    ### 📋 수급요건
    - **조건 1** : 신청일이 속한 달의 직전 달 1일부터 신청일까지 근무일 수가 총 일수의 1/3 미만
    - **조건 2 (건설일용)** : 신청일 직전 14일간 근무 사실이 없어야 함 (신청일 제외)
    """)

    apply_date = st.date_input("📅 신청일 선택", value=current_datetime.date())
    date_range, start_date = get_date_range(apply_date)

    st.markdown("### ✅ 근무일 선택 (콤보박스)")
    date_options = [d.strftime("%Y-%m-%d (%a)") for d in date_range]
    selected_strs = st.multiselect("근무한 날짜를 선택하세요.", date_options)
    selected_dates = set(datetime.strptime(s.split()[0], "%Y-%m-%d").date() for s in selected_strs)

    total_days = len(date_range)
    worked_days = len(selected_dates)
    threshold = total_days / 3

    cond1 = worked_days < threshold

    fourteen_end = apply_date - timedelta(days=1)
    fourteen_start = fourteen_end - timedelta(days=13)
    worked_in_14 = any(
        d in selected_dates for d in [dt.date() for dt in pd.date_range(fourteen_start, fourteen_end)]
    )
    cond2 = not worked_in_14

    st.markdown("---")
    st.markdown("### ✅ 조건별 판정")

    cond1_text = (
        f"✅ 조건 1 충족: 근무일 수가 기준 미만입니다.\n"
        f"(총 {worked_days}일 / 기간 {total_days}일, 기준 {threshold:.1f}일)"
        if cond1 else
        f"❌ 조건 1 불충족: 근무일 수가 기준 이상입니다.\n"
        f"(총 {worked_days}일 / 기간 {total_days}일, 기준 {threshold:.1f}일)"
    )
    cond2_text = (
        f"✅ 조건 2 충족: 신청일 직전 14일간 근무 기록이 없습니다."
        if cond2 else
        f"❌ 조건 2 불충족: 신청일 직전 14일간({fourteen_start} ~ {fourteen_end}) 내 근무기록이 존재합니다."
    )
    st.markdown(cond1_text)
    st.markdown(cond2_text)

    suggestion_text = ""
    if not cond2:
        last_worked = max(
            (d for d in selected_dates if d < apply_date), default=None
        )
        if last_worked:
            suggested = last_worked + timedelta(days=15)
            suggestion_text = (
                f"📅 조건 2를 충족하려면 언제 신청해야 할까요?\n"
                f"✅ {suggested} 이후에 신청하면 조건 2를 충족할 수 있습니다."
            )
            st.markdown(suggestion_text)

    st.markdown("---")
    st.markdown("### 📌 최종 판단")

    general_text = (
        f"✅ 일반일용근로자: 신청 가능\n"
        f"수급자격 인정신청일이 속한 달의 직전 달 초일부터 신청일까지({start_date} ~ {apply_date}) "
        f"근무일 수가 총 일수의 1/3 미만으로 신청 가능합니다."
        if cond1 else
        f"❌ 일반일용근로자: 신청 불가\n"
        f"근무일 수가 총 일수의 1/3 이상으로 신청이 어렵습니다."
    )

    if cond1 or cond2:
        if cond1 and cond2:
            reason = f"조건 1과 조건 2 모두 충족하여 신청 가능합니다."
        elif cond1:
            reason = f"신청일 직전 14일간({fourteen_start} ~ {fourteen_end}) 근무기록은 있으나 조건 1을 충족하여 신청 가능합니다."
        else:
            reason = f"조건 1은 불충족하였으나 신청일 직전 14일간 근무기록이 없어 신청 가능합니다."
        construction_text = f"✅ 건설일용근로자: 신청 가능\n{reason}"
    else:
        construction_text = (
            f"❌ 건설일용근로자: 신청 불가\n"
            f"조건 1과 조건 2 모두 충족하지 않아 신청이 어렵습니다."
        )

    st.markdown(general_text)
    st.markdown(construction_text)

    result_text = "\n\n".join([
        cond1_text,
        cond2_text,
        suggestion_text,
        general_text,
        construction_text
    ])

    # ✅ DB에 저장
    c.execute(
        'INSERT INTO logs (timestamp, apply_date, worked_days, total_days, cond1, cond2, email) VALUES (?, ?, ?, ?, ?, ?, ?)',
        (datetime.now(KST).isoformat(), str(apply_date), worked_days, total_days, int(cond1), int(cond2), None)
    )
    conn.commit()

    # ✅ PDF 다운로드
    if st.button("📄 PDF로 저장"):
        pdf = render_pdf(result_text)
        st.download_button("📎 PDF 다운로드", data=pdf, file_name="result.pdf", mime="application/pdf")

    # ✅ 이메일 전송
    email = st.text_input("📧 결과를 이메일로 받을 이메일 주소")
    if st.button("✉️ 이메일 발송") and email:
        send_email(email, result_text)
        st.success(f"{email} 로 발송되었습니다.")

    st.markdown("### 📋 결과 복사")
    st.code(result_text, language='markdown')

    st.info(f"이 모의계산기는 참고용입니다. 현재 버전: {APP_VERSION}")

if __name__ == "__main__":
    daily_worker_eligibility_app()
