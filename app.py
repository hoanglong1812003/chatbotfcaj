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
    
    # Chuẩn hóa tên người với ngôi xưng
    NAME_MAP = {
        "anh Hưng": "Nguyễn Gia Hưng",
        "sư phụ Hưng": "Nguyễn Gia Hưng",
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
    
    # Chuẩn hóa FCAJ
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
        cache_folder="/tmp/huggingface"
    )
    return FAISS.load_local(
        "vectorstore",
        embeddings,
        allow_dangerous_deserialization=True
    )

@st.cache_resource
def setup_rag_chain():
    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0.1,
        groq_api_key=os.getenv("GROQ_API_KEY")
    )

    vectorstore = load_vectorstore()
    retriever = vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={"k": 5, "fetch_k": 10}
    )

    SYSTEM_PROMPT = """Bạn là trợ lý AI của cộng đồng First Cloud AI Journey (FCAJ) - AWS Vietnam.

THÔNG TIN VỀ FCAJ:
- First Cloud AI Journey (FCAJ) là cộng đồng học AWS và Cloud Computing tại Việt Nam
- Được thành lập bởi AWS Vietnam để hỗ trợ người học từ cơ bản đến nâng cao

ĐỘI ADMIN FCAJ (luôn sẵn sàng hỗ trợ hết mình):
- Sư phụ: Nguyễn Gia Hưng
- Đội trưởng: Lữ Hoàn Thiện
- Các admin: Trần Đại Vĩ, Huỳnh Hoàng Long, Phạm Hoàng Quy, Bùi Hoàng Việt, Đặng Thị Minh Thư, Lý Kiên Huy, Nguyễn Đỗ Thành Đạt

QUY TẮC TRẢ LỜI:
✅ Trả lời TỰ NHIÊN như đang nói chuyện
✅ Đi thẳng vào nội dung, KHÔNG nói "dựa trên tài liệu", "theo tài liệu"
✅ KHÔNG nhắc "Tài liệu 1, 2, 3..."

Khi được hỏi CHÍNH XÁC "Bạn là ai" hoặc "Bạn là ai?":
→ Trả lời: Tôi là trợ lý AI của cộng đồng First Cloud AI Journey (FCAJ)
→ KHÔNG cần tìm trong tài liệu

Khi được hỏi về FCAJ hoặc đội admin:
→ Trả lời dựa trên thông tin FCAJ và đội admin ở trên
→ KHÔNG cần tìm trong tài liệu

Khi được hỏi "[Tên người] là ai":
→ Tìm trong tài liệu bên dưới
→ Nếu KHÔNG có thông tin: "Hiện chưa có thông tin về người này trong tài liệu FCAJ"
→ KHÔNG suy đoán

Khi được hỏi về kiến thức khác:
→ Đọc thông tin bên dưới và trả lời TRỰC TIẾP
→ Nếu có: Trả lời ngắn gọn, bullet points
→ Nếu không có: "Hiện chưa có thông tin này trong tài liệu FCAJ"

VÍ DỤ:
❌ SAI: "Dựa trên tài liệu được cung cấp, FCAJ có 3 chương trình..."
✅ ĐÚNG: "FCAJ có 3 chương trình chính: ..."

❌ SAI: "Theo tài liệu 2, điểm trừ là..."
✅ ĐÚNG: "Điểm trừ khi đi trễ là..."
"""

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", """
Thông tin từ tài liệu:
{context}

Câu hỏi:
{question}
""")
    ])

    def format_docs(docs):
        if not docs:
            return ""
        return "\n\n".join(doc.page_content for doc in docs)

    rag_chain = (
        {
            "context": retriever | format_docs,
            "question": RunnablePassthrough()
        }
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
    page_title="First Cloud Journey Assistant",
    page_icon="☁️",
    layout="wide"
)

st.header("☁️ First Cloud Journey Assistant")
st.subheader("Chatbot hỗ trợ cộng đồng AWS Vietnam")

with st.sidebar:
    st.markdown("### 📘 Hướng dẫn")
    if st.button("🔄 Làm mới"):
        st.session_state.messages = []

if "messages" not in st.session_state:
    st.session_state.messages = []

# Hiển thị lời chào và gợi ý khi chưa có tin nhắn
if len(st.session_state.messages) == 0:
    with st.chat_message("assistant"):
        st.markdown("""
👋 Xin chào! Tôi là trợ lý AI của cộng đồng **First Cloud AI Journey (FCAJ)**.

Tôi có thể giúp bạn:
- 📚 Tìm hiểu về AWS và Cloud Computing
- 👥 Thông tin về FCAJ và đội admin
- 📊 Cách tính điểm và quy định chương trình
- ⚠️ Xử lý vi phạm và nội quy

Hãy thử các câu hỏi gợi ý bên dưới! 👇
        """)
    
    # Các nút gợi ý câu hỏi
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("👥 Đội admin FCAJ gồm những ai?"):
            st.session_state.messages.append({"role": "user", "content": "Đội admin FCAJ gồm những ai?"})
            st.rerun()
        
        if st.button("📊 Cách tính điểm như thế nào?"):
            st.session_state.messages.append({"role": "user", "content": "Cách tính điểm như thế nào?"})
            st.rerun()
    
    with col2:
        if st.button("☁️ FCAJ là gì?"):
            st.session_state.messages.append({"role": "user", "content": "FCAJ là gì?"})
            st.rerun()
        
        if st.button("⚠️ Xử lý vi phạm ra sao?"):
            st.session_state.messages.append({"role": "user", "content": "Xử lý vi phạm ra sao?"})
            st.rerun()

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# Xử lý câu hỏi từ button gợi ý
if len(st.session_state.messages) > 0:
    last_msg = st.session_state.messages[-1]
    if last_msg["role"] == "user":
        # Kiểm tra xem đã có response chưa
        if len(st.session_state.messages) == 1 or st.session_state.messages[-2]["role"] == "assistant":
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
