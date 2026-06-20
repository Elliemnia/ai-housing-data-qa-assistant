import os

import pandas as pd
import streamlit as st
from anthropic import Anthropic
from dotenv import load_dotenv


load_dotenv()


st.set_page_config(
    page_title="AI Housing Data Q&A Assistant",
    page_icon="🏠",
    layout="wide"
)


MONTH_ORDER = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]


def get_api_key():
    return os.getenv("ANTHROPIC_API_KEY")


def create_dataset_context(df):
    preview = df.head(10).to_string()
    columns = list(df.columns)
    shape = df.shape

    numeric_columns = df.select_dtypes(include=["number"]).columns.tolist()
    stats = (
        df[numeric_columns].describe().to_string()
        if numeric_columns
        else "No numeric columns available."
    )

    return f"""
Dataset shape: {shape[0]} rows and {shape[1]} columns

Columns:
{columns}

Dataset preview:
{preview}

Basic numeric statistics:
{stats}
"""


def answer_question_with_claude(dataset_context, user_question):
    api_key = get_api_key()

    if not api_key:
        raise ValueError("Anthropic API key is missing.")

    client = Anthropic(api_key=api_key)

    prompt = f"""
You are an AI data analyst helping a public-sector or nonprofit stakeholder understand a housing dataset.

Dataset context:
{dataset_context}

User question:
{user_question}

Answer the question using only the dataset context provided.

Rules:
- Do not invent facts.
- If the dataset does not contain enough information, say that clearly.
- Explain the answer in plain English.
- Include specific values from the dataset when possible.
- Keep the answer useful for a non-technical stakeholder.
- Include a short recommendation when appropriate.
"""

    message = client.messages.create(
        model="claude-3-5-haiku-latest",
        max_tokens=700,
        messages=[{"role": "user", "content": prompt}]
    )

    return message.content[0].text


def get_dataset_health(df):
    missing_values = int(df.isna().sum().sum())
    duplicate_rows = int(df.duplicated().sum())

    return f"""
### Dataset Health Check

- Total rows: **{df.shape[0]}**
- Total columns: **{df.shape[1]}**
- Missing values: **{missing_values}**
- Duplicate rows: **{duplicate_rows}**

### Notes

- This check helps identify basic data quality issues before using AI-generated analysis.
- Larger datasets should also be reviewed for inconsistent categories, date formatting issues, and outliers.
"""


def demo_answer(user_question):
    question = user_question.lower()

    if "zip" in question or "highest" in question:
        return """
Based on the sample dataset, ZIP code **90064** has the highest total eviction activity in this sample.

This suggests that 90064 may be one of the areas with repeated eviction-related activity. However, because this is a small demo dataset, a larger historical dataset would be needed before making policy or program decisions.
"""

    if "cause" in question or "common" in question:
        return """
The most common eviction cause in the sample dataset appears to be **Rent Owed**.

This is connected to records labeled as **Nonpayment of Rent**, which appear repeatedly across multiple months. This may indicate tenant financial stress, but more complete data would be needed for a stronger conclusion.
"""

    if "month" in question or "trend" in question:
        return """
The sample data includes records from January through May.

The highest month in the sample appears to be **March**, while rent-related records appear across several months. This suggests that Nonpayment of Rent is not limited to a single period in this sample.
"""

    if "risk" in question or "recommend" in question:
        return """
A housing program manager may want to monitor ZIP codes with repeated eviction activity, especially where Rent Owed appears multiple times.

Recommended next steps include reviewing a larger dataset, grouping cases by ZIP code and month, and identifying whether certain neighborhoods may need targeted tenant support or outreach.
"""

    return """
This dataset appears to contain housing or eviction-related records by ZIP code, notice type, eviction cause, case count, and month.

A useful next step would be to group records by ZIP code, eviction cause, or month to identify patterns for housing program staff.
"""


def prepare_monthly_cases(df):
    monthly_cases = df.groupby("month")["case_count"].sum().reset_index()
    monthly_cases["month"] = pd.Categorical(
        monthly_cases["month"],
        categories=MONTH_ORDER,
        ordered=True
    )
    return monthly_cases.sort_values("month")


def calculate_summary_metrics(df):
    total_cases = int(df["case_count"].sum()) if "case_count" in df.columns else 0

    top_zip = "N/A"
    top_zip_cases = 0
    if "zip_code" in df.columns and "case_count" in df.columns:
        zip_cases = df.groupby("zip_code")["case_count"].sum()
        top_zip = str(zip_cases.idxmax())
        top_zip_cases = int(zip_cases.max())

    top_cause = "N/A"
    top_cause_cases = 0
    if "eviction_cause" in df.columns and "case_count" in df.columns:
        cause_cases = df.groupby("eviction_cause")["case_count"].sum()
        top_cause = str(cause_cases.idxmax())
        top_cause_cases = int(cause_cases.max())

    top_month = "N/A"
    top_month_cases = 0
    if "month" in df.columns and "case_count" in df.columns:
        monthly_cases = df.groupby("month")["case_count"].sum()
        top_month = str(monthly_cases.idxmax())
        top_month_cases = int(monthly_cases.max())

    return {
        "total_cases": total_cases,
        "top_zip": top_zip,
        "top_zip_cases": top_zip_cases,
        "top_cause": top_cause,
        "top_cause_cases": top_cause_cases,
        "top_month": top_month,
        "top_month_cases": top_month_cases,
    }


def render_sidebar():
    with st.sidebar:
        st.title("About this tool")
        st.write(
            "This app helps public-sector and nonprofit teams ask plain-English "
            "questions about housing datasets."
        )

        st.markdown("### How to use")
        st.markdown(
            """
1. Upload a CSV file  
2. Review charts and dataset health  
3. Choose or type a question  
4. Generate an AI-style answer  
5. Download the answer for notes or reporting  
"""
        )

        st.markdown("### Designed for")
        st.markdown(
            """
- Housing departments  
- Nonprofit teams  
- Civic tech projects  
- Program managers  
- Non-technical stakeholders  
"""
        )

        st.info(
            "Demo mode is available when Claude API credits are not configured."
        )


def render_summary_cards(df):
    metrics = calculate_summary_metrics(df)

    st.subheader("Key Metrics")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Cases", metrics["total_cases"])
    col2.metric("Top ZIP Code", metrics["top_zip"], f"{metrics['top_zip_cases']} cases")
    col3.metric("Top Cause", metrics["top_cause"], f"{metrics['top_cause_cases']} cases")
    col4.metric("Highest Month", metrics["top_month"], f"{metrics['top_month_cases']} cases")


def render_quick_insights(df):
    metrics = calculate_summary_metrics(df)

    st.subheader("Quick Data Insights")

    st.markdown(
        f"""
- The dataset contains **{metrics["total_cases"]} total cases**.
- The ZIP code with the highest activity is **{metrics["top_zip"]}** with **{metrics["top_zip_cases"]} cases**.
- The most common eviction cause is **{metrics["top_cause"]}** with **{metrics["top_cause_cases"]} cases**.
- The month with the highest activity is **{metrics["top_month"]}** with **{metrics["top_month_cases"]} cases**.
"""
    )


def render_charts(df):
    st.subheader("Quick Visual Insights")

    chart_col1, chart_col2 = st.columns(2)

    if "month" in df.columns and "case_count" in df.columns:
        monthly_cases = prepare_monthly_cases(df)
        with chart_col1:
            st.write("Cases by Month")
            st.bar_chart(monthly_cases, x="month", y="case_count")

    if "zip_code" in df.columns and "case_count" in df.columns:
        zip_cases = (
            df.groupby("zip_code")["case_count"]
            .sum()
            .sort_values(ascending=False)
            .reset_index()
        )
        with chart_col2:
            st.write("Cases by ZIP Code")
            st.bar_chart(zip_cases, x="zip_code", y="case_count")

    if "eviction_cause" in df.columns and "case_count" in df.columns:
        cause_cases = (
            df.groupby("eviction_cause")["case_count"]
            .sum()
            .sort_values(ascending=False)
            .reset_index()
        )
        st.write("Cases by Eviction Cause")
        st.bar_chart(cause_cases, x="eviction_cause", y="case_count")


def render_app():
    render_sidebar()

    st.title("AI Housing Data Q&A Assistant")
    st.write(
        "Upload a housing CSV file, explore quick charts, check dataset health, "
        "and ask plain-English questions about the data."
    )

    uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

    if not uploaded_file:
        st.info("Upload a CSV file to begin.")
        return

    df = pd.read_csv(uploaded_file)

    st.subheader("Data Preview")
    st.dataframe(df.head(), use_container_width=True)

    render_summary_cards(df)
    render_charts(df)
    render_quick_insights(df)

    with st.expander("Dataset Health Check"):
        st.markdown(get_dataset_health(df))

    st.subheader("Ask a Question About the Dataset")

    example_questions = [
        "Which ZIP codes have the highest eviction activity?",
        "What is the most common eviction cause?",
        "Summarize trends by month.",
        "Which areas may need additional support?",
        "What patterns should housing managers monitor?",
        "What risks do you see in this dataset?",
        "Which notice type appears most frequently?",
        "What recommendations would you make?",
        "Are there any recurring issues?",
        "Explain the findings for non-technical stakeholders."
    ]

    selected_question = st.selectbox(
        "Choose an example question or write your own below:",
        example_questions
    )

    user_question = st.text_area(
        "Your question:",
        value=selected_question
    )

    if "qa_history" not in st.session_state:
        st.session_state.qa_history = []

    if st.button("Ask AI Assistant"):
        dataset_context = create_dataset_context(df)

        try:
            with st.spinner("Analyzing dataset with Claude..."):
                answer = answer_question_with_claude(
                    dataset_context,
                    user_question
                )

            response_type = "AI Answer"

        except Exception:
            st.warning(
                "Live Claude response is currently unavailable. Showing a demo "
                "answer so the workflow can still be tested."
            )

            answer = demo_answer(user_question)
            response_type = "Demo AI Answer"

        st.subheader(response_type)
        st.markdown(answer)

        st.download_button(
            label="Download Answer as Text",
            data=answer,
            file_name="housing_ai_answer.txt",
            mime="text/plain"
        )

        st.session_state.qa_history.append(
            {"question": user_question, "answer": answer}
        )

    if st.session_state.qa_history:
        st.subheader("Q&A History")
        for index, item in enumerate(reversed(st.session_state.qa_history), start=1):
            with st.expander(f"Question {index}: {item['question']}"):
                st.markdown(item["answer"])


if __name__ == "__main__":
    render_app()