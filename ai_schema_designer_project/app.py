
import streamlit as st
import pandas as pd
import json

from tracking_plan import (
    generate_tracking_plan,
    tracking_plan_to_markdown,
    tracking_plan_to_dbt_yaml,
    generate_sample_events,
)

st.set_page_config(
    page_title="AI Schema Designer for Event Tracking",
    layout="wide",
)

st.title("🧠 AI Schema Designer for Event Tracking")
st.write(
    """
    This tool helps product and analytics teams design clean, consistent tracking plans
    for new features. Describe your feature, list key actions, and generate:
    - A structured event tracking plan
    - Suggested dbt schema YAML
    - Synthetic sample events
    - Taxonomy checks
    """
)

with st.form("tracking_form"):
    feature_name = st.text_input("Feature name", value="workspace_sharing")
    feature_description = st.text_area(
        "Feature description",
        value=(
            "Allow workspace owners to invite collaborators, manage permissions, and "
            "share access links to specific bases or views."
        ),
        height=80,
    )
    platform = st.selectbox("Primary platform", ["web", "mobile", "desktop", "api"])
    key_actions_text = st.text_area(
        "Key user actions (one per line)",
        value="open share dialog\ncopy share link\ninvite collaborator\nchange permission\nremove collaborator",
        height=100,
    )
    funnel_stages_text = st.text_input(
        "Funnel stages (comma-separated)",
        value="view,start,complete",
    )
    n_samples = st.slider("Number of sample events to generate", 5, 50, 10)

    submitted = st.form_submit_button("Generate tracking plan")

if submitted:
    key_actions = [line.strip() for line in key_actions_text.splitlines() if line.strip()]
    funnel_stages = [s.strip() for s in funnel_stages_text.split(",") if s.strip()]

    plan = generate_tracking_plan(
        feature_name=feature_name,
        feature_description=feature_description,
        key_actions=key_actions,
        platform=platform,
        funnel_stages=funnel_stages,
    )

    md = tracking_plan_to_markdown(plan)
    dbt_yaml = tracking_plan_to_dbt_yaml(plan)
    samples = generate_sample_events(plan, n=n_samples)
    samples_df = pd.DataFrame(samples)

    tab1, tab2, tab3, tab4 = st.tabs(
        ["📋 Tracking Plan", "📦 dbt Schema YAML", "🧪 Sample Events", "⚠ Taxonomy Checks"]
    )

    with tab1:
        st.subheader("Tracking Plan (Markdown)")
        st.code(md, language="markdown")

    with tab2:
        st.subheader("Suggested dbt Schema (YAML)")
        st.code(dbt_yaml, language="yaml")

    with tab3:
        st.subheader("Synthetic Sample Events")
        st.dataframe(samples_df, use_container_width=True)
        st.download_button(
            "Download sample events as JSON",
            data=json.dumps(samples, indent=2),
            file_name=f"{feature_name}_sample_events.json",
            mime="application/json",
        )
        st.download_button(
            "Download sample events as CSV",
            data=samples_df.to_csv(index=False),
            file_name=f"{feature_name}_sample_events.csv",
            mime="text/csv",
        )

    with tab4:
        st.subheader("Taxonomy Checks")
        if plan["taxonomy_issues"]:
            for issue in plan["taxonomy_issues"]:
                st.markdown(f"- ❗ {issue}")
        else:
            st.success("No taxonomy issues detected. Event names and properties look consistent!")
else:
    st.info("Fill in the form above and click **Generate tracking plan** to get started.")
