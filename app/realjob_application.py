# moel/app/realjob_application.py
import streamlit as st

def realjob_application_app():
    st.markdown("""
        <h3 style='color: #333333;'>
            실업인정 대상 기간 중 국내 체류 일정이 있으신가요? (※ 고용24에서 비대면 인정 가능 구간/사유에서 일자사유 세부 설정 필요)
        </h3>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 3])
    with col1:
        st.checkbox("구직활동이 없는 경우 체크하세요")
    with col2:
        st.button("구직활동 등록")

    st.markdown("### 구직활동 *")
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("구직번호 *", value="G10000H1EE-003")
            st.text_input("구직일자 *", value="YYYY-MM-DD")
            st.selectbox("사유체크 *", ["사유체크를 입력하세요", "옵션1", "옵션2"])
        with col2:
            st.button("사유체크를 입력하세요", key="reason_check")

    st.markdown("### 연락처/활동내역 *")
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.selectbox("연락처 *", ["010-1234-5678", "010-9876-5432"])
            st.radio("이메일 주소 입력", ["입력 안함", "입력함"])
            st.text_input("이메일", placeholder="이메일을 입력하세요")
        with col2:
            st.selectbox("직업번호", ["직업을 선택하세요", "선택1", "선택2"])

    st.markdown("### 재취업 활동 *")
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.selectbox("활동 *", ["활동을 선택하세요", "활동1", "활동2"])
            st.selectbox("구체적 활동", ["구체적 활동을 선택하세요", "활동1", "활동2"])
        with col2:
            st.button("모집 정보 입력", key="recruit_info")

    st.markdown("### 수급자격 *")
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.selectbox("수급자격", ["수급자격을 선택하세요", "자격1", "자격2"])
        with col2:
            st.button("입력자격", key="input_qualification")

    st.button("등록하기")
    st.button("등록/취소 버튼없기", key="cancel")

    with st.sidebar:
        st.markdown("### 고용보험 B.S. 공공 유저관리")
        st.write("PRBCON-SK 08")
        st.write("~SOCK-SK 01")
        st.markdown("#### 실업급여실행 *")
        st.selectbox("연락처", ["연락처를 선택하세요", "010-1234-5678"])
        st.markdown("#### 근로자 *")
        st.selectbox("활동", ["활동을 선택하세요", "활동1", "활동2"])
        st.markdown("#### SS 08 *")
        st.selectbox("GREIND", ["GREIND 선택", "옵션1", "옵션2"])
