import streamlit as st
from app.daily_worker_eligibility import run_daily_worker_eligibility_app

def main():
    st.set_page_config(page_title="일용근로자 수급자격 모의계산기", layout="centered")
    run_daily_worker_eligibility_app()

if __name__ == "__main__":
    main()
