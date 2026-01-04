import os
from langchain_community.document_loaders import PyPDFLoader, TextLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

def process_documents():
    # Load documents từ thư mục data
    loader = DirectoryLoader('data/', glob="**/*.pdf", loader_cls=PyPDFLoader)
    documents = loader.load()
    
    # Thêm text files
    text_loader = DirectoryLoader('data/', glob="**/*.txt", loader_cls=TextLoader, loader_kwargs={'encoding': 'utf-8'})
    text_docs = text_loader.load()
    documents.extend(text_docs)
    
    # Chia nhỏ documents với chunk size nhỏ hơn để tìm kiếm chính xác hơn
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    texts = text_splitter.split_documents(documents)
    
    # Tạo embeddings với model tốt hơn
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )
    
    # Tạo vector store
    vectorstore = FAISS.from_documents(texts, embeddings)
    vectorstore.save_local("vectorstore")
    
    print(f"Đã xử lý {len(texts)} chunks từ {len(documents)} tài liệu")

if __name__ == "__main__":
    process_documents()