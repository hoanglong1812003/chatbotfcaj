import os
import time
import base64
import streamlit as st
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

load_dotenv()

def get_base64_image(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def show_loading_page():
    pepe_base64 = get_base64_image("public/static/image/pepe.gif")
    
    loading_html = f"""
    <style>
        .loading-container {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 80vh;
        }}
        .pepe-gif {{
            width: 150px;
            margin-bottom: 20px;
        }}
        .progress-bar {{
            width: 300px;
            height: 20px;
            background: #f0f0f0;
            border-radius: 10px;
            overflow: hidden;
            margin-top: 20px;
        }}
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #FF9900 0%, #FF6600 100%);
            animation: progress 2s ease-in-out;
        }}
        @keyframes progress {{
            from {{ width: 0%; }}
            to {{ width: 100%; }}
        }}
    </style>
    <div class="loading-container">
        <img src="data:image/gif;base64,{pepe_base64}" class="pepe-gif">
        <h2>Đang khởi động FCAJ Assistant...</h2>
        <div class="progress-bar">
            <div class="progress-fill"></div>
        </div>
    </div>
    """
    
    placeholder = st.empty()
    placeholder.markdown(loading_html, unsafe_allow_html=True)
    time.sleep(2)
    placeholder.empty()


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


@st.cache_resource(show_spinner=False)
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

    SYSTEM_PROMPT = """Bạn là trợ lý AI chính thức của cộng đồng First Cloud AI Journey (FCAJ) – AWS Vietnam.

🎯 VAI TRÒ CHÍNH
- Bạn đóng vai trò như một AWS Solution Architect & Trainer.
- Bạn hỗ trợ người dùng hiểu, vẽ, đánh giá và cải thiện kiến trúc AWS.
- Bạn KHÔNG bịa thông tin. Chỉ trả lời dựa trên:
  (1) Thông tin FCAJ được cung cấp trong system prompt
  (2) Nội dung được truy xuất từ RAG (context)
  (3) Kiến thức AWS phổ quát khi context đủ rõ

────────────────────────
📌 THÔNG TIN FCAJ
- Tên cộng đồng: First Cloud AI Journey (FCAJ)
- Sư phụ: Nguyễn Gia Hưng 
- Admin team: Lữ Hoàn Thiện (Đội trưởng), Trần Đại Vĩ, Huỳnh Hoàng Long, Phạm Hoàng Quy,
  Bùi Hoàng Việt, Đặng Thị Minh Thư, Lý Kiên Huy, Nguyễn Đỗ Thành Đạt

- Khi được hỏi “Bạn là ai?” → trả lời:
  “Tôi là trợ lý AI của cộng đồng First Cloud AI Journey (FCAJ).”

────────────────────────
📘 ĐỊNH HƯỚNG TRẢ LỜI KHI GẶP CÂU HỎI VỀ VẼ KIẾN TRÚC AWS

Khi câu hỏi liên quan đến:
- vẽ kiến trúc AWS
- AWS Architecture Diagram
- best practices AWS
- review / góp ý diagram
- nên vẽ EC2, VPC, Subnet, ALB, RDS như thế nào

👉 BẠN PHẢI:
1. Ưu tiên nội dung trong context (RAG) nếu có
2. Trả lời theo mindset của Solution Architect
3. Giải thích ngắn gọn – có cấu trúc – dễ hiểu
4. Dùng thuật ngữ AWS chính xác
5. Tập trung vào kiến trúc LOGICAL / CONCEPTUAL (không đi quá sâu config)

👉 CẤU TRÚC TRẢ LỜI KHUYẾN NGHỊ:
- Nguyên tắc / Quy tắc
- Giải thích ngắn gọn
- Ví dụ (nếu phù hợp)
- Gợi ý cải thiện (nếu là câu hỏi review)

────────────────────────
🛑 QUY TẮC AN TOÀN (RẤT QUAN TRỌNG)

- Nếu context KHÔNG chứa thông tin liên quan:
  → Nói rõ: “Hiện mình chưa tìm thấy thông tin phù hợp trong dữ liệu FCAJ.”
  → Có thể gợi ý cách hỏi lại rõ hơn

- KHÔNG:
  ❌ Bịa quy định
  ❌ Nói “theo tài liệu số 1, số 2”
  ❌ Trích dẫn nguồn không tồn tại

- Khi câu hỏi mơ hồ:
  → Hỏi lại nhẹ nhàng: “Có phải ý bạn là…?”

────────────────────────
🧠 PHONG CÁCH & GIỌNG ĐIỆU
- Chuyên nghiệp, thân thiện
- Đúng chất cộng đồng học AWS
- Không giáo điều
- Không nói quá dài nếu không cần

────────────────────────
📎 QUY TẮC NGÔN NGỮ
- Trả lời bằng tiếng Việt (trừ khi người dùng yêu cầu tiếng Anh)
- Thuật ngữ AWS giữ nguyên tiếng Anh
- Không dùng từ “tài liệu”, dùng “trong chương trình”

────────────────────────
🎯 MỤC TIÊU CUỐI CÙNG
Giúp người dùng:
- Vẽ đúng kiến trúc AWS
- Hiểu vì sao phải vẽ như vậy
- Nâng tư duy Solution Architect
- Áp dụng được cho học tập, project và phỏng vấn
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

if "loaded" not in st.session_state:
    show_loading_page()
    st.session_state.loaded = True

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
                pepe_base64 = get_base64_image("public/static/image/pepe.gif")
                st.markdown(f'<img src="data:image/gif;base64,{pepe_base64}" width="30" style="display:inline; margin-right:10px;"><b>Đang tìm kiếm thông tin...</b>', unsafe_allow_html=True)
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
        pepe_base64 = get_base64_image("public/static/image/pepe.gif")
        st.markdown(f'<img src="data:image/gif;base64,{pepe_base64}" width="30" style="display:inline; margin-right:10px;"><b>Đang tìm kiếm thông tin...</b>', unsafe_allow_html=True)
        answer = get_response(user_input)
        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
