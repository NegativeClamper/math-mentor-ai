import os
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma

load_dotenv()

PERSIST_DIR = "./chroma_db"
DATA_PATH = "data/math_formulas.txt"

def build_knowledge_base():
    if not os.path.exists(DATA_PATH):
        print("Error: Data file not found.")
        return

    loader = TextLoader(DATA_PATH)
    documents = loader.load()

    text_splitter = CharacterTextSplitter(
        separator="\n## ", chunk_size=300, chunk_overlap=0
    )
    docs = text_splitter.split_documents(documents)

    # CHANGE: Using Google's Embedding Model
    embedding_fn = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    
    db = Chroma.from_documents(docs, embedding_fn, persist_directory=PERSIST_DIR)
    print(f"✅ Knowledge Base built with {len(docs)} chunks using Gemini Embeddings.")

def retrieve_context(query, k=2):
    embedding_fn = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    db = Chroma(persist_directory=PERSIST_DIR, embedding_function=embedding_fn)
    results = db.similarity_search(query, k=k)
    return "\n".join([doc.page_content for doc in results])

if __name__ == "__main__":
    build_knowledge_base()