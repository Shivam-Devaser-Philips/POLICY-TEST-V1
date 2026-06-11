import os
from typing import Dict, List, Optional

try:
    import dotenv
except ImportError:
    dotenv = None
import pandas as pd
import plotly.express as px
import streamlit as st

from analytics import (
    add_impact_labels,
    build_recommendations,
    generate_executive_summary,
    summarize_by_section,
)
from comparison import compare_policy_clauses
from embeddings import create_embeddings, load_embedding_model
from parser import load_document, split_into_clauses
from rag import build_chat_prompt, build_vector_store, query_llm, search_vector_store
from reports import create_excel_report, create_pdf_report


st.set_page_config(page_title="Policy Intelligence Platform", layout="wide")
if dotenv:
    dotenv.load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL_NAME = os.getenv("GROQ_MODEL_NAME", "mixtral-8x7b-32768")
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq")
LLM_ENDPOINT = os.getenv("LLM_ENDPOINT", "")


@st.cache_resource
def get_embedding_model():
    return load_embedding_model(EMBEDDING_MODEL_NAME)


def initialize_session_state():
    state_defaults = {
        "old_text": "",
        "new_text": "",
        "old_clauses": pd.DataFrame(),
        "new_clauses": pd.DataFrame(),
        "comparison": pd.DataFrame(),
        "impact_df": pd.DataFrame(),
        "section_summary": pd.DataFrame(),
        "executive_summary": {},
        "vector_store": None,
        "chat_history": [],
    }
    for key, value in state_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def render_sidebar():
    st.sidebar.title("Policy Intelligence")
    page = st.sidebar.radio(
        "Navigation",
        ["Upload Documents", "Dashboard", "Comparison", "Search", "Chatbot", "Reports"],
    )
    st.sidebar.markdown("---")
    st.sidebar.write("Optional LLM settings can be configured in `.env`.")
    if GROQ_API_KEY:
        st.sidebar.success("LLM configured")
    else:
        st.sidebar.info("LLM not configured; generative AI features are disabled.")
    return page


def load_sample_documents():
    old_sample = (
        "1.1 Purpose:\nThis policy defines leave entitlement.\n"
        "1.2 Scope:\nApplies to all employees.\n"
        "2.1 Annual Leave:\nEmployees are entitled to 20 days of annual leave.\n"
    )
    new_sample = (
        "1.1 Purpose:\nThis policy defines leave entitlement and compliance requirements.\n"
        "1.2 Scope:\nApplies to all employees and contractors.\n"
        "2.1 Annual Leave:\nEmployees are entitled to 22 days of annual leave.\n"
        "2.2 Compliance:\nLeave policies must follow labor regulations.\n"
    )
    return old_sample, new_sample


def process_documents(old_doc, new_doc):
    old_clauses = split_into_clauses(old_doc)
    new_clauses = split_into_clauses(new_doc)
    model = get_embedding_model()
    if not old_clauses.empty:
        old_clauses["embedding"] = list(create_embeddings(old_clauses["clause"].tolist(), model))
    if not new_clauses.empty:
        new_clauses["embedding"] = list(create_embeddings(new_clauses["clause"].tolist(), model))
    comparison = compare_policy_clauses(old_clauses, new_clauses)
    comparison = add_impact_labels(comparison)
    exec_summary = generate_executive_summary(comparison)
    section_summary = summarize_by_section(comparison)
    impact_df = comparison[["old_section", "old_clause", "new_section", "new_clause", "change_type", "impact_level", "impact_reason"]].copy()
    return old_clauses, new_clauses, comparison, exec_summary, section_summary, impact_df


def render_upload_page():
    st.title("Upload Policy Documents")
    st.markdown(
        "Upload your old and new policy documents in PDF or DOCX format to compare changes, analyze impact, and build an AI-assisted report."
    )
    col1, col2 = st.columns(2)
    with col1:
        old_file = st.file_uploader("Upload old policy", type=["pdf", "docx"], key="old_upload")
    with col2:
        new_file = st.file_uploader("Upload new policy", type=["pdf", "docx"], key="new_upload")

    if st.button("Load sample documents"):
        st.session_state["old_text"], st.session_state["new_text"] = load_sample_documents()

    if old_file is not None:
        st.session_state["old_text"] = load_document(old_file)
    if new_file is not None:
        st.session_state["new_text"] = load_document(new_file)

    if st.session_state["old_text"] or st.session_state["new_text"]:
        with st.expander("Old Policy Preview"):
            st.text_area("Old policy text", st.session_state["old_text"], height=250)
        with st.expander("New Policy Preview"):
            st.text_area("New policy text", st.session_state["new_text"], height=250)

    if st.button("Process documents"):
        (
            st.session_state["old_clauses"],
            st.session_state["new_clauses"],
            st.session_state["comparison"],
            st.session_state["executive_summary"],
            st.session_state["section_summary"],
            st.session_state["impact_df"],
        ) = process_documents(st.session_state["old_text"], st.session_state["new_text"])

        if not st.session_state["comparison"].empty:
            st.success("Documents processed successfully. Navigate to the Dashboard or Comparison page.")
        else:
            st.warning("No clauses were extracted. Check the uploaded documents.")


def render_dashboard_page():
    st.title("Analytics Dashboard")
    summary = st.session_state["executive_summary"]
    if not summary:
        st.warning("Load and process documents first on the Upload Documents page.")
        return
    cols = st.columns(6)
    cols[0].metric("Total Clauses", summary.get("total_clauses", 0))
    cols[1].metric("Added", summary.get("added", 0), delta_color="normal")
    cols[2].metric("Deleted", summary.get("deleted", 0), delta_color="normal")
    cols[3].metric("Modified", summary.get("modified", 0), delta_color="normal")
    cols[4].metric("Unchanged", summary.get("unchanged", 0), delta_color="normal")
    high = len(st.session_state["comparison"][st.session_state["comparison"]["impact_level"] == "High Impact"])
    mid = len(st.session_state["comparison"][st.session_state["comparison"]["impact_level"] == "Medium Impact"])
    low = len(st.session_state["comparison"][st.session_state["comparison"]["impact_level"] == "Low Impact"])
    cols[5].metric("High Impact", high)

    chart_data = pd.DataFrame(
        [
            {"change_type": "Added", "count": summary.get("added", 0)},
            {"change_type": "Deleted", "count": summary.get("deleted", 0)},
            {"change_type": "Modified", "count": summary.get("modified", 0)},
            {"change_type": "Unchanged", "count": summary.get("unchanged", 0)},
        ]
    )
    fig = px.pie(chart_data, names="change_type", values="count", title="Change Distribution")
    st.plotly_chart(fig, use_container_width=True)

    impact_data = pd.DataFrame(
        [
            {"impact": "High Impact", "count": high},
            {"impact": "Medium Impact", "count": mid},
            {"impact": "Low Impact", "count": low},
        ]
    )
    fig2 = px.bar(impact_data, x="impact", y="count", title="Impact Distribution", text="count")
    st.plotly_chart(fig2, use_container_width=True)

    if not st.session_state["section_summary"].empty:
        fig3 = px.bar(
            st.session_state["section_summary"],
            x="section",
            y=["added", "deleted", "modified", "unchanged"],
            title="Changes by Section",
        )
        st.plotly_chart(fig3, use_container_width=True)


def render_comparison_page():
    st.title("Policy Comparison")
    if st.session_state["comparison"].empty:
        st.warning("Load and process documents first on the Upload Documents page.")
        return
    st.dataframe(st.session_state["comparison"], use_container_width=True)
    st.markdown("### Change Insights")
    st.write("Use the comparison table to identify additions, deletions, and modifications between old and new policy versions.")


def render_search_page():
    st.title("Semantic Search")
    if st.session_state["comparison"].empty:
        st.warning("Load and process documents first on the Upload Documents page.")
        return
    query = st.text_input("Search policies", placeholder="leave policy, compliance changes, employee benefits")
    if query:
        model = get_embedding_model()
        store = build_vector_store(
            pd.DataFrame(
                {
                    "clause": st.session_state["comparison"]["new_clause"].fillna("").tolist(),
                    "section": st.session_state["comparison"]["new_section"].fillna("General").tolist(),
                }
            ),
            model,
        )
        results = search_vector_store(store, query, model, top_k=5)
        st.dataframe(results, use_container_width=True)


def render_chatbot_page():
    st.title("RAG Chatbot")
    if st.session_state["comparison"].empty:
        st.warning("Load and process documents first on the Upload Documents page.")
        return
    question = st.text_input("Ask a question about policy changes", key="rag_question")
    if st.button("Ask"):
        model = get_embedding_model()
        store = build_vector_store(
            pd.DataFrame(
                {
                    "clause": st.session_state["comparison"]["new_clause"].fillna("").tolist(),
                    "section": st.session_state["comparison"]["new_section"].fillna("General").tolist(),
                }
            ),
            model,
        )
        results = search_vector_store(store, question, model, top_k=4)
        retrieved = results.to_dict("records")
        prompt = build_chat_prompt(question, retrieved)
        answer = query_llm(prompt, api_key=GROQ_API_KEY, provider=LLM_PROVIDER, model_name=GROQ_MODEL_NAME)
        st.session_state["chat_history"].append({"question": question, "answer": answer})

    for chat in st.session_state["chat_history"]:
        with st.expander(f"Q: {chat['question']}"):
            st.write(chat["answer"])


def render_reports_page():
    st.title("Reports")
    if st.session_state["comparison"].empty:
        st.warning("Load and process documents first on the Upload Documents page.")
        return
    recommendation_df = build_recommendations(st.session_state["comparison"])
    pdf_bytes = create_pdf_report(
        st.session_state["executive_summary"],
        st.session_state["section_summary"],
        st.session_state["comparison"],
        recommendation_df,
    )
    excel_bytes = create_excel_report(st.session_state["comparison"], st.session_state["comparison"], recommendation_df)

    st.download_button("Download PDF report", pdf_bytes, file_name="policy_report.pdf", mime="application/pdf")
    st.download_button("Download Excel report", excel_bytes, file_name="policy_report.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


def main():
    initialize_session_state()
    page = render_sidebar()

    if page == "Upload Documents":
        render_upload_page()
    elif page == "Dashboard":
        render_dashboard_page()
    elif page == "Comparison":
        render_comparison_page()
    elif page == "Search":
        render_search_page()
    elif page == "Chatbot":
        render_chatbot_page()
    elif page == "Reports":
        render_reports_page()


if __name__ == "__main__":
    main()
