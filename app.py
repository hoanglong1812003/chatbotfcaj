import os
import streamlit as st
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

load_dotenv()


def normalize_query(question: str) -> str:
    q = question.lower()

    NAME_MAP = {
        "anh hưng": "Nguyễn Gia Hưng",
        "sư phụ hưng": "Nguyễn Gia Hưng",
        "anh thiện": "Lữ Hoàn Thiện",
        "anh vĩ": "Trần Đại Vĩ",
        "anh long": "Huỳnh Hoàng Long",
        "anh quy": "Phạm Hoàng Quy",
        "anh việt": "Bùi Hoàng Việt",
        "chị thư": "Đặng Thị Minh Thư",
        "anh huy": "Lý Kiên Huy",
        "anh đạt": "Nguyễn Đỗ Thành Đạt",
    }

    for k, v in NAME_MAP.items():
        if k in q:
            q = q.replace(k, v)

    ENTITY_MAP = {
        "fcaj": "FCAJ",
        "fcj": "FCAJ",
        "first cloud journey": "FCAJ",
        "first cloud ai journey": "FCAJ",
    }
    for k, v in ENTITY_MAP.items():
        if k in q:
            q = q.replace(k, v)

    return q


@st.cache_resource
def load_vectorstore():
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        cache_folder="/tmp/huggingface",
    )

    if not os.path.exists("vectorstore/index.faiss"):
        st.error("⚠️ Vectorstore chưa được tạo. Vui lòng chạy `python process_docs.py`")
        st.stop()

    return FAISS.load_local(
        "vectorstore", embeddings, allow_dangerous_deserialization=True
    )


@st.cache_resource
def setup_rag_chain():
    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0.1,
        groq_api_key=os.getenv("GROQ_API_KEY"),
    )

    vectorstore = load_vectorstore()
    retriever = vectorstore.as_retriever(
        search_type="mmr", search_kwargs={"k": 5, "fetch_k": 10}
    )

    SYSTEM_PROMPT = """Bạn là trợ lý AI của cộng đồng First Cloud AI Journey (FCAJ) - AWS Vietnam.

ĐỘI ADMIN FCAJ: Sư phụ Nguyễn Gia Hưng, Đội trưởng Lữ Hoàn Thiện, Admin: Trần Đại Vĩ, Huỳnh Hoàng Long, Phạm Hoàng Quy, Bùi Hoàng Việt, Đặng Thị Minh Thư, Lý Kiên Huy, Nguyễn Đỗ Thành Đạt

NỘI DUNG PROJECT (báo cáo cuối khóa):
- Viết bằng 2 ngôn ngữ: tiếng Anh và tiếng Việt
- Các phần: Thông tin sinh viên, Worklog (Week 1-12), Proposal, Events Participated, Workshop, Self-evaluation, Sharing and Feedback

QUY ĐỊNH ĐIỂM DANH:
⏰ Trễ 15 phút sẽ bị trừ 0.05 điểm
⏰ Trễ 30 phút sẽ tính là vắng và trừ 0.1 điểm

QUY TẮC:
✅ Dùng "trong chương trình" thay vì "trong tài liệu"
✅ Khi không rõ: "Có phải ý bạn là...?"
✅ KHÔNG nhắc "Tài liệu 1, 2, 3..."

Khi hỏi "Bạn là ai": Tôi là trợ lý AI của FCAJ
Khi hỏi về FCAJ/admin/project: Dùng thông tin trên
Khi hỏi kiến thức khác: Tìm trong thông tin bên dưới
"""

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            ("human", "Thông tin:\n{context}\n\nCâu hỏi:\n{question}"),
        ]
    )

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs) if docs else ""

    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain


def get_response(question: str) -> str:
    try:
        normalized = normalize_query(question)
        rag_chain = setup_rag_chain()
        return rag_chain.invoke(normalized)
    except Exception as e:
        return f"⚠️ Lỗi: {str(e)}"


st.set_page_config(
    page_title="FCAJ Assistant",
    page_icon="☁️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://rules.fcjuni.com/",
        "About": "# FCAJ Chatbot v1.0",
    },
)

st.header("☁️ First Cloud AI Journey Assistant")
st.markdown(
    """
<div style='background: linear-gradient(90deg, #FF9900 0%, #FF6600 100%); 
            padding: 10px; border-radius: 10px; margin-bottom: 20px;'>
    <p style='color: white; text-align: center; margin: 0; font-size: 1.1em;'>
        🚀 Chatbot hỗ trợ cộng đồng FCAJ - AWS Vietnam
    </p>
</div>
""",
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("### 📚 Tài nguyên FCAJ")
    st.markdown(
        """
    📜 [Quy định FCAJ](https://rules.fcjuni.com/)
    
    🎥 [Kênh YouTube](https://www.youtube.com/@AWSStudyGroup)
    
    📚 [Tài liệu học tập](https://cloudjourney.awsstudygroup.com/)
    """
    )

    st.markdown("---")
    st.markdown("### 🛠️ Công cụ")

    if st.button("🔄 Làm mới cuộc trò chuyện"):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.markdown(
        """
    <div style='text-align: center; color: #666; font-size: 0.8em;'>
    🚀 Powered by FCAJ Team<br>
    © 2026 First Cloud AI Journey
    </div>
    """,
        unsafe_allow_html=True,
    )

if "messages" not in st.session_state:
    st.session_state.messages = []

if len(st.session_state.messages) == 0:
    with st.chat_message("assistant"):
        st.markdown(
            """
👋 Xin chào! Tôi là trợ lý AI của cộng đồng **First Cloud AI Journey (FCAJ)**.

Tôi có thể giúp bạn:
- 📚 Tìm hiểu về AWS và Cloud Computing
- 👥 Thông tin về FCAJ và đội admin
- 📊 Cách tính điểm và quy định chương trình
- ⚠️ Xử lý vi phạm và nội quy

Hãy thử các câu hỏi gợi ý bên dưới! 👇
        """
        )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("👥 Đội admin FCAJ gồm những ai?"):
            st.session_state.messages.append(
                {"role": "user", "content": "Đội admin FCAJ gồm những ai?"}
            )
            st.rerun()

        if st.button("📊 Cách tính điểm như thế nào?"):
            st.session_state.messages.append(
                {"role": "user", "content": "Cách tính điểm như thế nào?"}
            )
            st.rerun()

    with col2:
        if st.button("☁️ FCAJ là gì?"):
            st.session_state.messages.append({"role": "user", "content": "FCAJ là gì?"})
            st.rerun()

        if st.button("📝 Nội dung project là gì?"):
            st.session_state.messages.append(
                {"role": "user", "content": "Nội dung project là gì?"}
            )
            st.rerun()

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if len(st.session_state.messages) > 0:
    last_msg = st.session_state.messages[-1]
    if last_msg["role"] == "user":
        if (
            len(st.session_state.messages) == 1
            or st.session_state.messages[-2]["role"] == "assistant"
        ):
            with st.chat_message("assistant"):
                with st.spinner("🔍 Đang xử lý..."):
                    answer = get_response(last_msg["content"])
                    st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
            st.rerun()

user_input = st.chat_input("Hỏi về AWS, FCAJ...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("🔍 Đang xử lý..."):
            answer = get_response(user_input)
            st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
