"""
Checkpoint 4, Deliverable 16 - Application Interface

A Streamlit chat UI that wraps the Checkpoint 3 RAG logic (src/08_rag_app.py:
LangChain + Chroma + Gemini, with multi-turn memory) without changing it.
All retrieval / prompting / memory behaviour still lives in PathfinderSession;
this file only adds the web layer:

  * one PathfinderSession per browser session (st.session_state), so every
    visitor gets their own conversation memory
  * the Chroma index + embedding model + LLM client are loaded ONCE per
    server process (st.cache_resource), not on every message
  * friendly handling of the failure modes a public deployment actually hits
    (missing API key, Gemini quota / network errors)
  * light abuse protection, because a public URL backed by a free-tier API key
    is a quota-exhaustion target: per-session turn cap + max question length

Run locally:   streamlit run app/streamlit_app.py
In Docker:     see Dockerfile (port 7860, GEMINI_API_KEY injected at runtime)
"""

import importlib.util
import logging
import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
load_dotenv(ROOT / ".env")  # no-op in Docker: the key arrives as a real env var

MAX_TURNS = int(os.environ.get("MAX_TURNS_PER_SESSION", "30"))
MAX_QUESTION_CHARS = int(os.environ.get("MAX_QUESTION_CHARS", "500"))

EXAMPLE_QUESTIONS = [
    "What are the prerequisites for IS 104 System Analysis & Design?",
    "What's the GWA requirement for Latin honors?",
    "How many units can I enroll in if I'm on academic probation?",
    "What subjects are in first year first semester?",
    "What do I need before enrolling in Capstone Project I?",
    "Can you write me a haiku about databases?  (out-of-scope demo)",
]

logger = logging.getLogger("pathfinder.app")

st.set_page_config(page_title="Pathfinder - BSIS Academic Advisor", page_icon="🧭")


# --------------------------------------------------------------------------
# Backend loading (once per server process)
# --------------------------------------------------------------------------
def _load_module(name: str, path: Path):
    # The pipeline scripts are named 04_..., 08_... (not valid import names),
    # so load them by path - same pattern 07_ingest_pipeline.py already uses.
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@st.cache_resource(show_spinner="Loading the BSIS knowledge base...")
def load_backend():
    rag = _load_module("pathfinder_rag_app", SRC / "08_rag_app.py")
    if not rag.CHROMA_DIR.exists():
        # Local first run only. The Docker image ships with the index already
        # built (see Dockerfile builder stage), so this never triggers there.
        indexer = _load_module("pathfinder_indexer", SRC / "04_setup_vector_db.py")
        indexer.build_index()
    return rag, rag.get_vectorstore(), rag.get_llm()


def new_session(rag, vectorstore, llm):
    st.session_state.session = rag.PathfinderSession(vectorstore, llm)
    st.session_state.messages = []


# --------------------------------------------------------------------------
# UI helpers
# --------------------------------------------------------------------------
def render_details(meta: dict) -> None:
    with st.expander("Sources & retrieval details"):
        unique_sources = list(dict.fromkeys(meta["sources"]))
        st.markdown("**Documents retrieved:**")
        for source in unique_sources:
            st.markdown(f"- `{source}`")
        if meta["search_query"].strip() != meta["question"].strip():
            st.markdown(f"**Standalone query (resolved from chat memory):** {meta['search_query']}")
        if meta["term_filter"]:
            year, semester = meta["term_filter"]
            st.markdown(f"**Metadata filter applied:** Year {year}, Semester {semester}")


def render_history() -> None:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("meta"):
                render_details(message["meta"])


# --------------------------------------------------------------------------
# Page
# --------------------------------------------------------------------------
st.title("🧭 Pathfinder")
st.caption("A RAG-based academic advisor for BSIS students at Talibon Polytechnic College")

try:
    rag_module, vector_store, chat_model = load_backend()
except SystemExit as exc:  # get_llm() exits when GEMINI_API_KEY is missing
    st.error(f"Configuration problem: {exc}")
    st.stop()
except Exception:
    logger.exception("Backend failed to start")
    st.error("Pathfinder could not start (knowledge base or model failed to load). Check the server logs.")
    st.stop()

if "session" not in st.session_state:
    new_session(rag_module, vector_store, chat_model)

with st.sidebar:
    st.header("About")
    st.write(
        "Ask about BSIS course prerequisites, curriculum terms, grading/GWA, "
        "enrollment rules, and registrar/guidance services. Answers are "
        "grounded in the knowledge base and cite their source documents. "
        "Follow-up questions work - Pathfinder remembers the conversation."
    )
    st.warning(
        "Curriculum checklist and TPC website content are real. Course "
        "descriptions and academic policies are **simulated** for this class "
        "project - confirm anything important with the Registrar or Program Head."
    )
    st.subheader("Try an example")
    for example in EXAMPLE_QUESTIONS:
        if st.button(example, use_container_width=True):
            st.session_state.pending = example.split("  (")[0]
    st.divider()
    if st.button("🗑️ New conversation", use_container_width=True):
        new_session(rag_module, vector_store, chat_model)
        st.rerun()
    st.caption(f"Model: `{rag_module.MODEL_NAME}` · Retrieval: top-{rag_module.K} chunks (Chroma, cosine)")

render_history()

typed = st.chat_input("Ask about your BSIS curriculum or policies...")
question = typed or st.session_state.pop("pending", None)

if question:
    question = question.strip()
    turns_used = sum(1 for m in st.session_state.messages if m["role"] == "user")

    if len(question) > MAX_QUESTION_CHARS:
        st.warning(f"Please keep questions under {MAX_QUESTION_CHARS} characters.")
    elif turns_used >= MAX_TURNS:
        st.warning(
            f"This conversation reached the {MAX_TURNS}-question limit. "
            "Use **New conversation** in the sidebar to continue."
        )
    else:
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner("Searching the knowledge base..."):
                try:
                    result = st.session_state.session.ask(question)
                except Exception:
                    # ask() only appends to memory after a successful LLM call,
                    # so a failed turn leaves the conversation state clean.
                    logger.exception("Gemini / retrieval call failed")
                    st.session_state.messages.pop()  # drop the unanswered question
                    st.error(
                        "Pathfinder couldn't reach the language model (it may be rate-limited "
                        "or offline). Please wait a moment and try again."
                    )
                    st.stop()
            st.markdown(result["answer"])
            meta = {
                "question": result["question"],
                "search_query": result["search_query"],
                "term_filter": result["term_filter"],
                "sources": result["sources"],
            }
            render_details(meta)

        st.session_state.messages.append(
            {"role": "assistant", "content": result["answer"], "meta": meta}
        )
