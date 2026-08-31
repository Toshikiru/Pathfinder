"""
Checkpoint 3, Deliverable 13 (supporting evidence) - LlamaIndex Comparison Demo
Builds a SEPARATE, LlamaIndex-native index over the same processed corpus
(its own SimpleDirectoryReader -> SentenceSplitter -> VectorStoreIndex
pipeline, not our hand-rolled chunker) and runs the same demo queries used
in 04_setup_vector_db.py, so docs/Framework_Comparison_Note.md can cite real,
matched output instead of a written-only opinion.

This is comparison-only: it is NOT wired into the production app
(08_rag_app.py uses LangChain - see that file's docstring and the comparison
note for why). It writes to its own Chroma collection
("pathfinder_llamaindex_demo") in the same chroma_db directory, so it never
touches or rebuilds the production "pathfinder_bsis_advisor" collection.
"""

import os
from pathlib import Path

import chromadb
from dotenv import load_dotenv
from llama_index.core import Settings, SimpleDirectoryReader, StorageContext, VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.vector_stores.chroma import ChromaVectorStore

ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DIR = ROOT / "data" / "processed"
CHROMA_DIR = ROOT / "data" / "chroma_db"
COLLECTION_NAME = "pathfinder_llamaindex_demo"
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
MODEL_NAME = "gemini-3.5-flash-lite"

# Same demo queries 04_setup_vector_db.py runs against our hand-rolled
# chunker/Chroma setup, so results are directly comparable.
DEMO_QUERIES = [
    "What are the prerequisites for IS 104 System Analysis & Design?",
    "How many units can I enroll in while on academic probation?",
    "Who is the program head of BSIS?",
    "What is required to enroll in Capstone Project I?",
    "What is the GWA requirement for Latin honors?",
]


def build_index() -> VectorStoreIndex:
    documents = SimpleDirectoryReader(
        input_dir=str(PROCESSED_DIR),
        recursive=True,
        required_exts=[".txt"],
        filename_as_id=True,
    ).load_data()

    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    collection = client.create_collection(COLLECTION_NAME)
    vector_store = ChromaVectorStore(chroma_collection=collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    # chunk_size is in TOKENS (not chars) - 128 tokens keeps node granularity
    # comparable to our hand-rolled chunker's ~500-char/sentence-grouped chunks.
    Settings.node_parser = SentenceSplitter(chunk_size=128, chunk_overlap=20)
    Settings.embed_model = HuggingFaceEmbedding(model_name=EMBEDDING_MODEL_NAME)

    index = VectorStoreIndex.from_documents(documents, storage_context=storage_context)
    print(f"Indexed {len(documents)} documents into LlamaIndex's own node-parsed "
          f"'{COLLECTION_NAME}' collection.")
    return index


def main() -> None:
    load_dotenv(ROOT / ".env")
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key or api_key == "your-gemini-api-key-here":
        raise SystemExit(
            "GEMINI_API_KEY not set. Copy .env.example to .env and paste your "
            "free key from https://aistudio.google.com/apikey"
        )

    Settings.llm = GoogleGenAI(model=MODEL_NAME, api_key=api_key)
    index = build_index()
    query_engine = index.as_query_engine(similarity_top_k=3)

    print("\n" + "=" * 90)
    print("LLAMAINDEX QUERY ENGINE DEMO (same queries as 04_setup_vector_db.py)")
    print("=" * 90)
    for q in DEMO_QUERIES:
        response = query_engine.query(q)
        print(f"\nQuery: {q}")
        print(f"Answer: {response.response}")
        for node in response.source_nodes:
            source = node.metadata.get("file_name", "?")
            preview = node.get_content()[:140].replace("\n", " ")
            print(f"  [{node.score:.4f}] {source}: \"{preview}...\"")


if __name__ == "__main__":
    main()
