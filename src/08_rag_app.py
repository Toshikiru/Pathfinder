"""
Checkpoint 3, Deliverables 11 + 12 - RAG Application with Conversational Memory
The CP3 working application: a LangChain-orchestrated RAG chat app over the
existing Chroma index (built in 04_setup_vector_db.py), grounded with the
CP2 `live_advisor` prompt (src/prompts.py), that holds a real multi-turn
conversation instead of answering single isolated queries.

Framework choice: LangChain, not LlamaIndex, for the production app - see
docs/Framework_Comparison_Note.md for the full reasoning (short version:
LangChain composes with our *existing* Chroma collection/prompts without
re-indexing anything; LlamaIndex wants to own ingestion end-to-end via its
own chunker, which src/09_llamaindex_comparison.py demos separately).

Memory design: a plain list of LangChain BaseMessage objects
(HumanMessage/AIMessage), appended each turn. Before retrieval, if there is
prior history, one small LLM call condenses the latest question into a
standalone query using that history (e.g. "How many units is it?" ->
"How many units is IS 104 System Analysis & Design?"). This is the
hand-rolled equivalent of LangChain's create_history_aware_retriever, done
manually so the app isn't coupled to higher-level chain-constructor APIs
that have shifted across LangChain's major versions.

Requires GEMINI_API_KEY in .env (see .env.example), same as 06_api_integration_demo.py.
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Optional

import chromadb
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_core.embeddings import Embeddings
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from sentence_transformers import SentenceTransformer

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from prompts import PROMPTS  # noqa: E402

CHROMA_DIR = ROOT / "data" / "chroma_db"
COLLECTION_NAME = "pathfinder_bsis_advisor"
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
MODEL_NAME = "gemini-3.5-flash-lite"
TRANSCRIPT_PATH = ROOT / "docs" / "_rag_app_demo_transcripts.md"
K = 4


class MiniLMEmbeddings(Embeddings):
    """LangChain Embeddings wrapper around the *exact* sentence-transformers
    model/settings 04_setup_vector_db.py used to build the index, so query
    embeddings land in the same space as what's already stored (chromadb's
    SentenceTransformerEmbeddingFunction normalizes by default; MiniLM also
    L2-normalizes internally regardless - see docs/Distance_Metric_Comparison.md)."""

    def __init__(self, model_name: str = EMBEDDING_MODEL_NAME):
        self.model = SentenceTransformer(model_name)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self.model.encode(texts, normalize_embeddings=True).tolist()

    def embed_query(self, text: str) -> List[float]:
        return self.model.encode([text], normalize_embeddings=True)[0].tolist()


def get_vectorstore() -> Chroma:
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    return Chroma(
        client=client,
        collection_name=COLLECTION_NAME,
        embedding_function=MiniLMEmbeddings(),
    )


_ORDINAL_WORDS = {
    "1st": 1, "first": 1, "one": 1,
    "2nd": 2, "second": 2, "two": 2,
    "3rd": 3, "third": 3, "three": 3,
    "4th": 4, "fourth": 4, "four": 4,
}
_YEAR_RE = re.compile(
    r"\b(1st|first|one|2nd|second|two|3rd|third|three|4th|fourth|four)\s*year\b", re.I
)
_SEM_RE = re.compile(
    r"\b(1st|first|one|2nd|second|two)\s*sem(?:ester)?\b", re.I
)


def detect_term(question: str) -> tuple[Optional[int], Optional[int]]:
    """Every curriculum term-checklist chunk shares near-identical header/table
    boilerplate ("BSIS Curriculum Checklist - Year X - ... Semester, Program:
    Bachelor of Science..."), so a generic phrasing like "first year first
    sem" can lose to other terms' near-duplicate chunks on pure embedding
    similarity - the distinguishing year/semester tokens are a tiny fraction
    of the chunk. When the question names both a year and a semester
    explicitly, detect them so retrieval can filter by the year/semester
    metadata 04_setup_vector_db.py now tags each curriculum chunk with,
    instead of relying on that fuzzy signal alone."""
    year_match = _YEAR_RE.search(question)
    sem_match = _SEM_RE.search(question)
    year = _ORDINAL_WORDS.get(year_match.group(1).lower()) if year_match else None
    semester = _ORDINAL_WORDS.get(sem_match.group(1).lower()) if sem_match else None
    if semester is not None and semester > 2:
        semester = None  # only two regular semesters exist per year in this curriculum
    return year, semester


def get_llm() -> ChatGoogleGenerativeAI:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key or api_key == "your-gemini-api-key-here":
        raise SystemExit(
            "GEMINI_API_KEY not set. Copy .env.example to .env and paste your "
            "free key from https://aistudio.google.com/apikey"
        )
    return ChatGoogleGenerativeAI(model=MODEL_NAME, google_api_key=api_key)


def extract_text(content) -> str:
    """gemini-3.5-flash-lite via langchain-google-genai sometimes returns
    `.content` as a string and sometimes as a list of content blocks
    (e.g. [{'type': 'text', 'text': '...', 'extras': {...}}]) - normalize
    to plain text either way."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                parts.append(block.get("text", ""))
            elif isinstance(block, str):
                parts.append(block)
        return "".join(parts)
    return str(content)


CONDENSE_INSTRUCTIONS = SystemMessage(content=(
    "Rewrite the latest user question as a standalone question that makes "
    "sense without the prior conversation, using the conversation history "
    "to resolve any pronoun, ellipsis, or implicit reference (e.g. 'it', "
    "'that course', 'what about X'). Do not answer the question. Respond "
    "with ONLY the rewritten standalone question, nothing else."
))


class PathfinderSession:
    """One conversation: holds message history and wires retrieval -> LLM."""

    def __init__(self, vectorstore: Chroma, llm: ChatGoogleGenerativeAI):
        self.vectorstore = vectorstore
        self.llm = llm
        self.history: List[BaseMessage] = []

    def _condense_question(self, question: str) -> str:
        if not self.history:
            return question
        messages = [CONDENSE_INSTRUCTIONS, *self.history, HumanMessage(content=question)]
        standalone = extract_text(self.llm.invoke(messages).content).strip()
        return standalone or question

    @staticmethod
    def _format_context(docs) -> str:
        return "\n\n---\n\n".join(f"[{d.metadata['source']}]\n{d.page_content}" for d in docs)

    def ask(self, question: str) -> dict:
        # search_query is also the standalone, reference-resolved question
        # (e.g. "it" -> "IS 104 System Analysis & Design"). Using it for the
        # QUESTION line too - not just retrieval - matters: without this, the
        # generation step can see the raw pronoun in isolation and ask for
        # clarification even though the resolved CONTEXT already answers it.
        search_query = self._condense_question(question)

        # When the question names a specific year AND semester explicitly,
        # filter retrieval to that term's metadata instead of relying on
        # embedding similarity alone - see detect_term()'s docstring for why
        # that similarity signal is unreliable across near-duplicate term
        # headers.
        year, semester = detect_term(search_query)
        term_filter = (
            {"$and": [{"year": year}, {"semester": semester}]}
            if year is not None and semester is not None
            else None
        )
        docs = self.vectorstore.similarity_search(search_query, k=K, filter=term_filter)
        context = self._format_context(docs)

        turn_prompt = HumanMessage(content=f"CONTEXT:\n{context}\n\nQUESTION: {search_query}")
        messages = [SystemMessage(content=PROMPTS["live_advisor"]), *self.history, turn_prompt]
        response = self.llm.invoke(messages)
        answer = extract_text(response.content)

        self.history.append(HumanMessage(content=question))
        self.history.append(AIMessage(content=answer))

        return {
            "question": question,
            "search_query": search_query,
            "term_filter": (year, semester) if term_filter else None,
            "sources": [d.metadata["source"] for d in docs],
            "answer": answer,
        }


# Multi-turn scripted demo: 8 turns covering deliverable 14's requirements
# (>=5 realistic queries, grounded answers, one out-of-scope refusal), plus
# three deliberate follow-ups (turns 2, 5, 8) that only make sense if
# conversational memory + condensed retrieval are actually working. Turns 7-8
# specifically exercise the year/semester metadata filter in detect_term() -
# without it, "first year first sem" loses to other terms' near-identical
# header chunks on embedding similarity alone (a real failure this fix
# addresses; see 04_setup_vector_db.py's TERM_FILENAME_RE comment).
SCRIPTED_DEMO_TURNS = [
    "What are the prerequisites for IS 104 System Analysis & Design?",
    "How many units is it?",
    "What's the GWA requirement for Latin honors?",
    "Can you write me a haiku about databases instead?",
    "What about CC 105 - what does that one require?",
    "How many units can I enroll in if I'm on academic probation?",
    "How many subjects are there in first year first sem?",
    "What about second sem?",
]


def run_scripted_demo() -> None:
    load_dotenv(ROOT / ".env")
    session = PathfinderSession(get_vectorstore(), get_llm())

    lines = [
        "# RAG Application Demo Transcripts (Checkpoint 3)\n",
        f"Model: `{MODEL_NAME}` via `langchain-google-genai`, retrieval via `langchain-chroma` "
        f"over the existing Chroma index. Each turn shows the standalone (memory-resolved) "
        f"search query actually used for retrieval, so it's visible when conversational "
        f"memory changed what was searched for.\n",
    ]

    for i, question in enumerate(SCRIPTED_DEMO_TURNS, 1):
        print(f"\n{'=' * 90}\nTurn {i}\n{'=' * 90}")
        print(f"Question: {question}")
        result = session.ask(question)
        print(f"Standalone search query: {result['search_query']}")
        print(f"Retrieved: {result['sources']}")
        print(f"\nAnswer:\n{result['answer']}")

        lines.append(f"\n## Turn {i}\n")
        lines.append(f"**Question:** {question}\n")
        if result["search_query"] != question:
            lines.append(f"**Standalone search query (memory-resolved):** {result['search_query']}\n")
        if result["term_filter"]:
            year, semester = result["term_filter"]
            lines.append(f"**Year/semester filter applied:** Year {year}, Semester {semester}\n")
        lines.append(f"**Retrieved sources:** {', '.join(result['sources'])}\n")
        lines.append(f"**Answer:**\n\n> {result['answer'].replace(chr(10), chr(10) + '> ')}\n")

    TRANSCRIPT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n\nSaved transcripts to {TRANSCRIPT_PATH}")


def live_chat_loop() -> None:
    load_dotenv(ROOT / ".env")
    session = PathfinderSession(get_vectorstore(), get_llm())

    print(f"\n{'=' * 90}\nPATHFINDER - ask about TPC's BSIS program (multi-turn, remembers context)\n{'=' * 90}")
    print("(type 'quit', 'exit', or an empty line to stop)\n")

    while True:
        try:
            question = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if not question or question.lower() in {"quit", "exit"}:
            print("Exiting.")
            break

        result = session.ask(question)
        print(f"[retrieved: {result['sources']}]")
        print(f"Pathfinder: {result['answer']}\n")


if __name__ == "__main__":
    if "--demo" in sys.argv:
        run_scripted_demo()
    else:
        live_chat_loop()
