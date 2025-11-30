
# AI Schema Designer for Event Tracking

This project is an AI-inspired helper for product and analytics teams to design clean, consistent tracking schemas
for new product features. It is designed to mirror the type of work an Analytics Engineer at companies like Airtable might do:
structuring events, enforcing taxonomy, and generating analytics-ready schemas.

>  Concept: "Given a feature description, generate a tracking plan, dbt-style schema YAML, synthetic events, and basic taxonomy checks."

## What it does

- Takes **feature name**, **description**, **platform**, and **key user actions**
- Generates:
  - A **tracking plan** with event names, descriptions, and when they should fire
  - Suggested **event properties** (user_id, workspace_id, timestamp, error_code, etc.)
  - A **dbt `schema.yml`-style** configuration for modeling events downstream
  - **Synthetic sample events** as JSON/CSV for testing or mocking
  - **Taxonomy warnings** (e.g., non-snake_case names, duplicates, missing required fields)

The current version uses rule-based logic for schema design, but can easily be extended to call an LLM
(OpenAI, Anthropic, etc.) to:
- Propose better event names
- Suggest additional properties tailored to the feature
- Generate narrative explanations or documentation

## How to run locally

1. Create and activate a virtual environment (optional but recommended):

```bash
python -m venv .venv
source .venv/bin/activate  # on Windows: .venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the Streamlit app:

```bash
streamlit run app.py
```

4. Your browser will open at something like:

```
http://localhost:8501
```

## How you might extend this with AI

Right now, `tracking_plan.py` uses deterministic, rule-based logic.
To turn this into a full AI-powered assistant, you could:

- Add an LLM client (e.g., OpenAI) and send:
  - The feature description
  - Example tracking plans
  - Company-specific naming conventions

- Ask the model to:
  - Propose event names and descriptions
  - Suggest additional properties and enumerations
  - Generate narrative documentation for PMs and engineers

From there, the LLM suggestions can be merged with the deterministic checks,
ensuring both **creativity** (from AI) and **reliability** (from validation rules).

## Files

- `app.py` — Streamlit UI
- `tracking_plan.py` — Core logic for generating plans, YAML, and synthetic events
- `requirements.txt` — Python dependencies
- `README.md` — Project overview and usage

## How to showcase this project

You can:

- Upload this entire folder as a **.zip** to Google Drive and share a link
- Or put it on **GitHub** and share the repo URL
- Record a short **Loom video** walking through:
  - A feature description example
  - The generated tracking plan
  - The dbt YAML and sample events
  - How this would help a product/analytics team move faster

This project demonstrates:

- Product analytics thinking (events, funnels, key actions)
- Analytics engineering skills (schema design, dbt-style YAML, data quality)
- AI-readiness (clear room to plug in LLMs for smarter automation)
- Initiative and end-to-end ownership
