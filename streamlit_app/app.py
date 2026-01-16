import streamlit as st
import requests

BACKEND_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Compliance Checker", layout="wide")
st.title("Compliance Checker (PDF/DOCX + Regulations PDF)")

tab1, tab2 = st.tabs(["1) Regulations Ingest", "2) Contract Compliance Check"])

# ------------------- Tab 1: Regulations Ingest -------------------
with tab1:
    st.subheader("Upload Regulations PDF (Vector DB Knowledge Base)")
    st.write("Tip: Use a small PDF initially for faster ingestion testing.")

    reg_file = st.file_uploader("Upload Regulations PDF", type=["pdf"])

    colA, colB = st.columns(2)
    with colA:
        reset = st.checkbox("Reset existing regulations before ingesting", value=True)

    with colB:
        max_chunks = st.slider(
            "Max chunks to embed (speed control)",
            min_value=50,
            max_value=800,
            value=300,
            step=50
        )

    if st.button("Ingest Regulations"):
        if reg_file is None:
            st.error("Please upload a Regulations PDF first.")
        else:
            files = {"file": (reg_file.name, reg_file.getvalue(), "application/pdf")}
            params = {"reset": str(reset).lower(), "max_chunks": max_chunks}

            with st.spinner("Embedding regulations into ChromaDB..."):
                try:
                    res = requests.post(
                        f"{BACKEND_URL}/regulations/ingest",
                        files=files,
                        params=params,
                        timeout=600
                    )
                except Exception as e:
                    st.error(f"Request failed: {e}")
                    st.stop()

            if res.status_code == 200:
                st.success("Regulations embedded successfully!")
                st.json(res.json())
            else:
                st.error(f"Error {res.status_code}")
                st.text(res.text)

    st.markdown("---")
    if st.button("Check Vector DB Count"):
        try:
            count_res = requests.get(f"{BACKEND_URL}/db/count", timeout=60)
            st.json(count_res.json())
        except Exception as e:
            st.error(f"Could not fetch DB count: {e}")


# ------------------- Tab 2: Contract Compliance -------------------
with tab2:
    st.subheader("Upload Contract (PDF/DOCX) and Check Compliance")

    contract_file = st.file_uploader("Upload Contract File", type=["pdf", "docx"])

    top_k = st.slider(
        "Top-K rules to retrieve per clause",
        min_value=1,
        max_value=5,
        value=2,
        step=1
    )

    if st.button("Check Compliance"):
        if contract_file is None:
            st.error("Please upload a contract file first.")
        else:
            files = {"file": (contract_file.name, contract_file.getvalue())}
            params = {"top_k": top_k}

            with st.spinner("Generating detailed compliance report..."):
                try:
                    res = requests.post(
                        f"{BACKEND_URL}/compliance/upload",
                        files=files,
                        params=params,
                        timeout=600
                    )
                except Exception as e:
                    st.error(f"Request failed: {e}")
                    st.stop()

            if res.status_code != 200:
                st.error(f"Error {res.status_code}")
                st.text(res.text)
                st.stop()

            data = res.json()

            st.success("Compliance report generated successfully!")

            # ---------------- Summary ----------------
            st.subheader("Overall Summary")
            st.json(data.get("summary", {}))

            # ---------------- Results ----------------
            st.subheader("Clause-by-Clause Findings")
            results = data.get("results", [])
            if not results:
                st.warning("No clauses detected. Ensure the contract has numbered clauses (1., 2., 3., etc.)")
                st.stop()

            for idx, r in enumerate(results, start=1):
                st.markdown("---")
                st.markdown(f"## Clause {idx}")

                st.markdown("### Clause Text")
                st.write(r.get("clause", ""))

                col1, col2, col3 = st.columns(3)
                col1.metric("Status", r.get("status", ""))
                col2.metric("Risk Level", r.get("risk_level", ""))
                col3.metric("Rules Retrieved", len(r.get("matched_rules", [])))

                st.markdown("### Reason (Why this is compliant / non-compliant)")
                st.write(r.get("reason", ""))

                st.markdown("### Risk / Impact")
                st.write(r.get("risk_impact", ""))

                if r.get("rectification_steps"):
                    st.markdown("### Rectification Steps (How to fix it)")
                    for step in r["rectification_steps"]:
                        st.write("-", step)

                if r.get("recommended_contract_changes"):
                    st.markdown("### Recommended Contract Changes")
                    for c in r["recommended_contract_changes"]:
                        st.write("-", c)

                if r.get("rewritten_clause"):
                    st.markdown("### Suggested Rewritten Clause (Fix)")
                    st.code(r["rewritten_clause"])

                with st.expander("Rule Mapping (why & what violated)"):
                    for m in r.get("rule_mapping", []):
                        st.write("Rule:", m.get("rule_excerpt", ""))
                        st.write("Relevance:", m.get("relevance", ""))
                        st.write("Violation:", m.get("violation", False))
                        st.markdown("---")

                with st.expander("Show retrieved rule excerpts"):
                    for mr in r.get("matched_rules", []):
                        st.write("-", mr)
