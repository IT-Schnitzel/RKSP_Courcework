import streamlit as st

def load_css():
    try:
        with open("web_client/styles.css", "r") as f:
            css = f.read()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.markdown("""
        <style>
            .main-header {
                background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
                padding: 2rem 2rem 1.5rem 2rem;
                border-radius: 0 0 24px 24px;
                margin: -1rem -1rem 2rem -1rem;
                color: white;
            }
            .main-header h1 {
                font-size: 2rem;
                font-weight: 700;
                margin: 0;
            }
            .main-header p {
                margin: 0.5rem 0 0 0;
                opacity: 0.9;
            }
            .card {
                background: white;
                border-radius: 12px;
                padding: 1.5rem;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                border: 1px solid #E2E8F0;
                height: 100%;
                text-align: center;
            }
            .card-title {
                font-size: 0.875rem;
                font-weight: 600;
                color: #64748B;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                margin-bottom: 0.5rem;
            }
            .card-value {
                font-size: 2rem;
                font-weight: 700;
                color: #1E293B;
                margin: 0;
            }
            .card-sub {
                font-size: 0.875rem;
                color: #64748B;
                margin-top: 0.5rem;
            }
        </style>
        """, unsafe_allow_html=True)

def header(title, subtitle=None):
    html = f"""
    <div class="main-header">
        <h1>{title}</h1>
        {f'<p>{subtitle}</p>' if subtitle else ''}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def status_badge(status):
    colors = {
        "pending": "#FEF3C7",
        "in_progress": "#DBEAFE",
        "completed": "#D1FAE5",
        "cancelled": "#FEE2E2",
        "archived": "#E5E7EB"
    }
    text_colors = {
        "pending": "#92400E",
        "in_progress": "#1E40AF",
        "completed": "#065F46",
        "cancelled": "#991B1B",
        "archived": "#4B5563"
    }
    bg = colors.get(status, "#E5E7EB")
    tc = text_colors.get(status, "#4B5563")
    return f'<span style="display:inline-block; padding:0.25rem 0.75rem; border-radius:9999px; font-size:0.75rem; font-weight:600; background:{bg}; color:{tc};">{status}</span>'

def priority_badge(priority):
    colors = {
        "low": "#D1FAE5",
        "medium": "#FEF3C7",
        "high": "#FDE68A",
        "urgent": "#FCA5A5",
        "critical": "#EF4444"
    }
    text_colors = {
        "low": "#065F46",
        "medium": "#92400E",
        "high": "#92400E",
        "urgent": "#991B1B",
        "critical": "#FFFFFF"
    }
    bg = colors.get(priority, "#E5E7EB")
    tc = text_colors.get(priority, "#4B5563")
    return f'<span style="display:inline-block; padding:0.25rem 0.75rem; border-radius:9999px; font-size:0.75rem; font-weight:600; background:{bg}; color:{tc};">{priority}</span>'