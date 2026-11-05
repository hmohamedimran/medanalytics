
"""
app.py
------
MEDANALYTIX - Healthcare Data Intelligence Platform
Main application entry point.
"""

import streamlit as st

# --------------------------------------------------
# 1. PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="MEDANALYTIX | Healthcare Data Intelligence Platform",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------
# 2. IMPORT PROJECT MODULES
# --------------------------------------------------

from modules.ui_helper import (
    inject_custom_css,
    render_sidebar,
    render_page_header,
    check_dataset_or_warn
)

from modules.data_quality import calculate_data_quality_score
from modules.healthcare_analytics import analyze_amoxicillin_distribution

from modules.eda_engine import (
    plot_numerical_distribution,
    plot_categorical_distribution
)


# --------------------------------------------------
# 3. HELPER FUNCTIONS
# --------------------------------------------------

def safe_number(value, default=0):
    """Safely convert values to numeric display."""
    try:
        return int(value) if value is not None else default
    except (ValueError, TypeError):
        return default


def safe_percentage(value):
    """Safely format percentage values."""
    try:
        return round(float(value), 2)
    except (ValueError, TypeError):
        return 0.0


# --------------------------------------------------
# 4. INITIALIZE APPLICATION
# --------------------------------------------------

try:
    inject_custom_css()
    render_sidebar()

    render_page_header(
        title="MEDANALYTIX",
        subtitle=(
            "Healthcare Data Intelligence Platform "
            "&bull; Advanced Clinical Analytics & Data Quality Audit"
        ),
        tag="MCA Healthcare Analytics Platform"
    )

except Exception as e:
    st.error(f"Application initialization error: {e}")
    st.stop()


# --------------------------------------------------
# 5. DATASET STATUS
# --------------------------------------------------

try:
    df, metadata = check_dataset_or_warn()

except Exception as e:
    st.error(f"Dataset loading error: {e}")
    st.stop()


# --------------------------------------------------
# 6. MAIN DASHBOARD
# --------------------------------------------------

if df is not None and metadata is not None:

    try:
        quality_score, grade, breakdown = (
            calculate_data_quality_score(df)
        )

        # Safe metadata extraction
        total_rows = safe_number(metadata.get("rows", len(df)))
        total_columns = safe_number(
            metadata.get("columns", len(df.columns))
        )

        numerical_columns = metadata.get("numerical_columns", [])
        categorical_columns = metadata.get("categorical_columns", [])

        total_missing = safe_number(
            metadata.get("total_missing", 0)
        )

        missing_percentage = safe_percentage(
            metadata.get("missing_percentage", 0)
        )

        duplicate_rows = safe_number(
            metadata.get("duplicate_rows", 0)
        )

        duplicate_percentage = safe_percentage(
            metadata.get("duplicate_percentage", 0)
        )

        memory_usage = metadata.get("memory_usage", "N/A")

        # --------------------------------------------------
        # 7. KPI DASHBOARD
        # --------------------------------------------------

        st.markdown(f"""
        <div class="kpi-grid">

            <div class="kpi-card">
                <div class="kpi-label">Total Records</div>
                <div class="kpi-value">{total_rows:,}</div>
                <div class="kpi-subtext">
                    Isolates / Patient observations
                </div>
            </div>

            <div class="kpi-card">
                <div class="kpi-label">Total Variables</div>
                <div class="kpi-value">{total_columns}</div>
                <div class="kpi-subtext">
                    {len(numerical_columns)} Num &bull;
                    {len(categorical_columns)} Cat
                </div>
            </div>

            <div class="kpi-card">
                <div class="kpi-label">Data Quality Score</div>
                <div class="kpi-value" style="color:#00f2fe;">
                    {quality_score}%
                </div>
                <div class="kpi-subtext">{grade}</div>
            </div>

            <div class="kpi-card">
                <div class="kpi-label">Missing Cells</div>
                <div class="kpi-value"
                     style="color:{'#10b981' if total_missing == 0 else '#f59e0b'};">
                    {total_missing:,}
                </div>
                <div class="kpi-subtext">
                    {missing_percentage}% of total data matrix
                </div>
            </div>

            <div class="kpi-card">
                <div class="kpi-label">Duplicate Rows</div>
                <div class="kpi-value"
                     style="color:{'#10b981' if duplicate_rows == 0 else '#f43f5e'};">
                    {duplicate_rows:,}
                </div>
                <div class="kpi-subtext">
                    {duplicate_percentage}% duplicate frequency
                </div>
            </div>

            <div class="kpi-card">
                <div class="kpi-label">Memory Footprint</div>
                <div class="kpi-value"
                     style="font-size:1.6rem; padding-top:4px;">
                    {memory_usage}
                </div>
                <div class="kpi-subtext">
                    Active RAM allocation
                </div>
            </div>

        </div>
        """, unsafe_allow_html=True)

        # --------------------------------------------------
        # 8. DASHBOARD LAYOUT
        # --------------------------------------------------

        col_left, col_right = st.columns(
            [1.1, 1],
            gap="medium"
        )

        # --------------------------------------------------
        # LEFT COLUMN
        # --------------------------------------------------

        with col_left:

            st.markdown("""
            <div class="med-card">
                <div class="med-card-header">
                    <div class="med-card-title">
                        🔍 Quick Data Preview
                    </div>
                    <span class="badge-cyan">
                        First 10 Observations
                    </span>
                </div>
            """, unsafe_allow_html=True)

            st.dataframe(
                df.head(10),
                use_container_width=True
            )

            st.markdown("</div>", unsafe_allow_html=True)

            # Operational audit trail
            recent_ops = st.session_state.get(
                "recent_operations", []
            )

            cleaning_log = st.session_state.get(
                "cleaning_log", []
            )

            st.markdown("""
            <div class="med-card">
                <div class="med-card-header">
                    <div class="med-card-title">
                        ⚡ Session Operational Audit Trail
                    </div>
                    <span class="badge-violet">
                        Live History
                    </span>
                </div>
            """, unsafe_allow_html=True)

            if recent_ops or cleaning_log:

                for op in reversed(recent_ops[-4:]):
                    st.markdown(
                        f"<div style='font-size:0.85rem; "
                        f"color:#cbd5e1; margin-bottom:6px;'>"
                        f"&bull; {op}</div>",
                        unsafe_allow_html=True
                    )

                for item in reversed(cleaning_log[-3:]):
                    action = item.get("action", "Operation")
                    details = item.get("details", "")

                    st.markdown(
                        f"<div style='font-size:0.85rem; "
                        f"color:#00f2fe; margin-bottom:6px;'>"
                        f"&bull; <b>{action}</b>: {details}</div>",
                        unsafe_allow_html=True
                    )

            else:
                st.markdown(
                    "<p style='color:#64748b; "
                    "font-size:0.85rem;'>"
                    "No active data operations recorded yet."
                    "</p>",
                    unsafe_allow_html=True
                )

            st.markdown("</div>", unsafe_allow_html=True)

        # --------------------------------------------------
        # RIGHT COLUMN
        # --------------------------------------------------

        with col_right:

            if metadata.get("is_amoxicillin_research", False):

                st.markdown("""
                <div class="med-card">
                    <div class="med-card-header">
                        <div class="med-card-title">
                            🔬 Amoxicillin Phenotype Overview
                        </div>
                        <span class="badge-violet">
                            Research Target
                        </span>
                    </div>
                """, unsafe_allow_html=True)

                try:
                    amox_counts, amox_fig = (
                        analyze_amoxicillin_distribution(df)
                    )

                    if amox_fig is not None:
                        st.plotly_chart(
                            amox_fig,
                            use_container_width=True
                        )
                    else:
                        st.info(
                            "No Amoxicillin distribution chart available."
                        )

                except Exception as chart_error:
                    st.warning(
                        f"Amoxicillin chart unavailable: {chart_error}"
                    )

                st.markdown("</div>", unsafe_allow_html=True)

            else:

                st.markdown("""
                <div class="med-card">
                    <div class="med-card-header">
                        <div class="med-card-title">
                            📈 Feature Distribution Preview
                        </div>
                        <span class="badge-cyan">
                            Univariate
                        </span>
                    </div>
                """, unsafe_allow_html=True)

                try:
                    if numerical_columns:

                        fig_preview = plot_numerical_distribution(
                            df,
                            numerical_columns[0]
                        )

                        if fig_preview is not None:
                            st.plotly_chart(
                                fig_preview,
                                use_container_width=True
                            )

                    elif categorical_columns:

                        fig_preview = plot_categorical_distribution(
                            df,
                            categorical_columns[0]
                        )

                        if fig_preview is not None:
                            st.plotly_chart(
                                fig_preview,
                                use_container_width=True
                            )

                    else:
                        st.info(
                            "No numerical or categorical columns available."
                        )

                except Exception as chart_error:
                    st.warning(
                        f"Distribution chart unavailable: {chart_error}"
                    )

                st.markdown("</div>", unsafe_allow_html=True)

        # --------------------------------------------------
        # 9. CLINICAL DISCLAIMER
        # --------------------------------------------------

        st.markdown("""
        <div class="clinical-disclaimer">
            <b>CLINICAL RESEARCH GOVERNANCE NOTICE:</b>
            All analytical telemetry and predictive markers displayed
            are computed strictly from retrospective experimental data.
            This platform is engineered for healthcare informatics
            research and hypothesis generation under MCA methodology,
            and does not constitute medical advice or automated
            clinical prescription.
        </div>
        """, unsafe_allow_html=True)

    except Exception as e:
        st.error(
            "An error occurred while rendering the MEDANALYTIX dashboard."
        )
        st.exception(e)
