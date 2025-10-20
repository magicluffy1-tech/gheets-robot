# --- 라이브러리 임포트 ---
import streamlit as st
import pandas as pd
from datetime import datetime

# --------------------------------------------------------------------------
# --- 1. 페이지 기본 설정 ---
# --------------------------------------------------------------------------
st.set_page_config(
    page_title="실시간 모둠별 질문 게시판 📝",
    page_icon="💎",
    layout="wide",
)

# --------------------------------------------------------------------------
# --- 2. 구글 시트 연결 ---
# --------------------------------------------------------------------------
# st.connection이 실패할 경우를 대비해 예외 처리를 추가하여 더 안정적으로 만듭니다.
try:
    conn = st.connection("gcs")
except Exception as e:
    st.error("🚨 Google Sheets에 연결할 수 없습니다. Secrets 설정을 다시 확인해주세요.")
    st.info("오류 상세 정보:", icon="👇")
    st.error(e)
    st.stop() # 연결에 실패하면 앱 실행을 중지합니다.

# --------------------------------------------------------------------------
# --- 3. 핵심 기능 함수 ---
# --------------------------------------------------------------------------
def add_question(group_name, question_text):
    """새로운 질문을 구글 시트에 추가하는 함수"""
    if not group_name or not question_text:
        st.warning("모둠 이름과 질문 내용을 모두 입력해주세요. 🧐")
        return

    new_row = pd.DataFrame([{
        "모둠": group_name,
        "질문 내용": question_text,
        "제출 시간": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }])
    
    conn.update(worksheet="Sheet1", data=new_row)
    st.success(f"'{group_name}'의 질문이 성공적으로 제출되었습니다! 🎉")

# --------------------------------------------------------------------------
# --- 4. 화면 UI 구성 (사이드바) ---
# --------------------------------------------------------------------------
with st.sidebar:
    st.header("🙋‍♀️ 질문 남기기")
    with st.form(key="question_form", clear_on_submit=True):
        group_name = st.text_input("모둠 이름", placeholder="예: 1모둠, 다이아팀")
        question_text = st.text_area("질문 내용", placeholder="여기에 질문을 상세히 작성해주세요.", height=150)
        submit_button = st.form_submit_button(label="질문 제출하기", use_container_width=True)

        if submit_button:
            add_question(group_name, question_text)
    
    st.info("💡 제출된 질문은 모든 사용자 화면에 실시간으로 공유됩니다.")

# --------------------------------------------------------------------------
# --- 5. 화면 UI 구성 (메인 화면) ---
# --------------------------------------------------------------------------
st.title("💎 실시간 모둠별 질문 게시판")
st.markdown("---")

# 구글 시트에서 전체 데이터를 읽어옵니다.
data = conn.read(worksheet="Sheet1", usecols=[0, 1, 2], ttl=5)
data = data.dropna(how="all") # 빈 행은 제거합니다.

if data.empty:
    st.info("아직 제출된 질문이 없습니다. 왼쪽 사이드바에서 첫 질문을 남겨보세요!")
else:
    # 모둠 이름으로 그룹화하여 오름차순 정렬
    grouped = data.groupby("모둠")
    for group_name, questions_df in sorted(grouped):
        question_count = len(questions_df)
        with st.expander(f"**{group_name}** (총 {question_count}개의 질문)"):
            # 제출 시간을 기준으로 최신순 정렬
            questions_df = questions_df.sort_values(by="제출 시간", ascending=False)
            for index, row in questions_df.iterrows():
                st.markdown(f"**Q.** {row['질문 내용']}")
                st.caption(f"_{row['제출 시간']}_")
                st.divider()