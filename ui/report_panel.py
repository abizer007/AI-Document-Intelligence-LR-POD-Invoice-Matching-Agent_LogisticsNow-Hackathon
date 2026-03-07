"""Streamlit UI for enterprise intelligence PDF generation."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

import pandas as pd
import streamlit as st

from modules.report_generator import generate_intelligence_report_pdf


REPORT_BYTES_KEY = "intelligence_report_pdf_bytes"
REPORT_NAME_KEY = "intelligence_report_file_name"


def render_report_panel(
    merged: pd.DataFrame,
    context: Dict[str, Any],
    fraud_flags: pd.DataFrame,
) -> None:
    """Render report generation panel with progress and downloadable PDF."""
    st.markdown("## Intelligence Report Generator")
    st.markdown(
        "Generate a full FreightLens logistics intelligence report including "
        "executive summary, shipment analytics, carrier and route risk, financial exposure, "
        "fraud analysis, and AI investigation insights."
    )

    generate_clicked = st.button("Generate Intelligence Report", type="primary", width="stretch")
    if generate_clicked:
        progress = st.progress(0.0)
        status = st.empty()

        def _progress_callback(value: float, message: str) -> None:
            progress.progress(float(value))
            status.info(f"AI is compiling your intelligence report... {message}")

        try:
            pdf_buffer = generate_intelligence_report_pdf(
                merged=merged,
                context=context,
                fraud_flags=fraud_flags,
                progress_callback=_progress_callback,
            )
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            filename = f"freightlens_intelligence_report_{timestamp}.pdf"
            st.session_state[REPORT_BYTES_KEY] = pdf_buffer.getvalue()
            st.session_state[REPORT_NAME_KEY] = filename
            progress.progress(1.0)
            status.success("Report generated successfully.")
        except Exception as exc:
            st.session_state.pop(REPORT_BYTES_KEY, None)
            st.session_state.pop(REPORT_NAME_KEY, None)
            progress.empty()
            status.error(f"Failed to generate report: {exc}")

    report_bytes = st.session_state.get(REPORT_BYTES_KEY)
    report_name = st.session_state.get(REPORT_NAME_KEY, "freightlens_intelligence_report.pdf")
    if report_bytes:
        st.download_button(
            label="Download Report",
            data=report_bytes,
            file_name=report_name,
            mime="application/pdf",
            width="stretch",
        )

