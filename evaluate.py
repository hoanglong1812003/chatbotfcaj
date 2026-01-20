import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

load_dotenv()

# Test cases: (câu hỏi, câu trả lời mong đợi chứa từ khóa)
TEST_CASES = [
    {
        "question": "Sư phụ FCAJ là ai?",
        "expected_keywords": ["Nguyễn Gia Hưng"],
        "category": "Thông tin cơ bản"
    },
    {
        "question": "Admin FCAJ gồm những ai?",
        "expected_keywords": ["Lữ Hoàn Thiện", "Trần Đại Vĩ"],
        "category": "Thông tin cơ bản"
    },
    {
        "question": "FCAJ là gì?",
        "expected_keywords": ["First Cloud", "Journey", "AWS"],
        "category": "Thông tin cơ bản"
    },
    {
        "question": "Cách tính điểm FCAJ như thế nào?",
        "expected_keywords": ["điểm"],
        "category": "Quy định"
    },
    {
        "question": "EC2 là gì?",
        "expected_keywords": ["EC2", "máy chủ", "server", "compute"],
        "category": "AWS Knowledge"
    },
]

def setup_rag_chain():
    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0.1,
        groq_api_key=os.getenv("GROQ_API_KEY"),
    )

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    )

    vectorstore = FAISS.load_local(
        "vectorstore", embeddings, allow_dangerous_deserialization=True
    )
    
    retriever = vectorstore.as_retriever(
        search_type="mmr", search_kwargs={"k": 5, "fetch_k": 10}
    )

    SYSTEM_PROMPT = """Bạn là trợ lý AI của FCAJ. Trả lời ngắn gọn, chính xác dựa trên context."""

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "Context:\n{context}\n\nCâu hỏi:\n{question}"),
    ])

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs) if docs else ""

    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain, retriever

def evaluate_response(response, expected_keywords):
    response_lower = response.lower()
    matched = sum(1 for keyword in expected_keywords if keyword.lower() in response_lower)
    return matched / len(expected_keywords) if expected_keywords else 0

def run_evaluation():
    print("🚀 Bắt đầu đánh giá chatbot...\n")
    
    rag_chain, retriever = setup_rag_chain()
    
    results = []
    total_score = 0
    
    for i, test in enumerate(TEST_CASES, 1):
        print(f"📝 Test {i}/{len(TEST_CASES)}: {test['category']}")
        print(f"❓ Câu hỏi: {test['question']}")
        
        # Lấy response
        response = rag_chain.invoke(test['question'])
        
        # Đánh giá
        score = evaluate_response(response, test['expected_keywords'])
        results.append({
            "question": test['question'],
            "category": test['category'],
            "response": response,
            "score": score,
            "expected": test['expected_keywords']
        })
        
        total_score += score
        
        print(f"💬 Trả lời: {response[:150]}...")
        print(f"✅ Điểm: {score*100:.1f}%")
        print(f"🔍 Từ khóa mong đợi: {', '.join(test['expected_keywords'])}\n")
        print("-" * 80 + "\n")
    
    # Tổng kết
    accuracy = (total_score / len(TEST_CASES)) * 100
    
    print("=" * 80)
    print("📊 KẾT QUẢ ĐÁNH GIÁ")
    print("=" * 80)
    print(f"✅ Tổng số test: {len(TEST_CASES)}")
    print(f"📈 Accuracy: {accuracy:.2f}%")
    print(f"⭐ Điểm trung bình: {total_score/len(TEST_CASES):.2f}/1.00")
    
    # Chi tiết theo category
    categories = {}
    for r in results:
        cat = r['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(r['score'])
    
    print("\n📋 Chi tiết theo danh mục:")
    for cat, scores in categories.items():
        avg = sum(scores) / len(scores) * 100
        print(f"  • {cat}: {avg:.1f}%")
    
    print("\n" + "=" * 80)
    
    # Lưu kết quả
    with open("evaluation_results.txt", "w", encoding="utf-8") as f:
        f.write(f"ACCURACY: {accuracy:.2f}%\n\n")
        for i, r in enumerate(results, 1):
            f.write(f"Test {i}:\n")
            f.write(f"Q: {r['question']}\n")
            f.write(f"A: {r['response']}\n")
            f.write(f"Score: {r['score']*100:.1f}%\n\n")
    
    print("💾 Kết quả đã được lưu vào evaluation_results.txt")

if __name__ == "__main__":
    run_evaluation()
