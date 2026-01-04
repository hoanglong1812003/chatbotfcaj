import os
import streamlit as st
from langchain_groq import ChatGroq
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from dotenv import load_dotenv

load_dotenv()

@st.cache_resource
def load_vectorstore():
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )
    vectorstore = FAISS.load_local("vectorstore", embeddings, allow_dangerous_deserialization=True)
    return vectorstore

@st.cache_resource
def setup_rag_chain():
    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0.2,
        groq_api_key=os.getenv("GROQ_API_KEY")
    )
    
    vectorstore = load_vectorstore()
    retriever = vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={"k": 5, "fetch_k": 10}
    )
    
    template = """Bạn là chatbot hỗ trợ cho cộng đồng First Cloud Journey của AWS.
Hãy phân tích kỹ thông tin được cung cấp và trả lời câu hỏi một cách chi tiết, chính xác.
Nếu không tìm thấy thông tin, hãy nói "Tôi không tìm thấy thông tin này trong tài liệu".

Thông tin từ tài liệu:
{context}

Câu hỏi: {question}

Trả lời chi tiết:"""
    
    prompt = ChatPromptTemplate.from_template(template)
    
    def format_docs(docs):
        return "\n\n".join(f"[Tài liệu {i+1}]:\n{doc.page_content}" for i, doc in enumerate(docs))
    
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return rag_chain

def get_response(query):
    try:
        rag_chain = setup_rag_chain()
        response = rag_chain.invoke(query)
        return response
    except Exception as e:
        return f"Lỗi: {str(e)}"

st.set_page_config(page_title="First Cloud Journey Assistant", page_icon="☁️", layout="wide")

st.header("🚀 First Cloud Journey Assistant")
st.subheader("Chatbot hỗ trợ cộng đồng AWS")

# Sidebar thông tin
with st.sidebar:
    st.markdown("### 📚 Hướng dẫn sử dụng")
    st.markdown("""
    - Đặt câu hỏi về AWS, Cloud Computing
    - Hỏi về các khóa học First Cloud Journey
    - Tìm hiểu về các dịch vụ AWS
    """)
    
    if st.button("🔄 Làm mới cuộc trò chuyện"):
        st.session_state.messages = []

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Hiển thị chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Hỏi về AWS, Cloud Computing..."):
    # Thêm user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Lấy response
    with st.chat_message("assistant"):
        with st.spinner("Đang tìm kiếm thông tin..."):
            response = get_response(prompt)
            st.markdown(response)
    
    # Thêm assistant message
    st.session_state.messages.append({"role": "assistant", "content": response})
