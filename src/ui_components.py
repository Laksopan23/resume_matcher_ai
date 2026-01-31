import streamlit as st

def brandbar(app_name: str, tagline: str):
    st.markdown(
        f"""
        <div class="brandbar">
          <div class="brand-left">
            <div class="logo">TR</div>
            <div>
              <p class="title">{app_name}</p>
              <p class="subtitle">{tagline}</p>
            </div>
          </div>
          <div style="display:flex; gap:8px; align-items:center;">
            <span style="font-size:12px; opacity:0.8; letter-spacing:0.01em;">Professional HR Mode</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def pill_html(decision: str, color: str = None) -> str:
    d = (decision or "").upper()
    cls = "review"
    label = "REVIEW"
    icon = "⚙️"
    
    if d == "SHORTLIST":
        cls, label, icon = "shortlist", "SHORTLIST", "✔"
    elif d == "REJECT":
        cls, label, icon = "reject", "REJECT", "✘"
    
    return f'<span class="pill {cls}">{icon} {label}</span>'

def pill(decision: str, color: str = None):
    st.markdown(pill_html(decision, color), unsafe_allow_html=True)

def kpis(items):
    """Render key performance indicators as styled metric cards."""
    blocks = []
    for label, value in items:
        blocks.append(
            f"""
            <div class="kpi">
              <div class="label">{label}</div>
              <div class="value">{value}</div>
            </div>
            """
        )
    st.markdown('<div class="kpis">' + "".join(blocks) + "</div>", unsafe_allow_html=True)

def chips(items, limit=18):
    """Render items as clean, modern chip/tag elements."""
    if not items:
        st.write("(none)")
        return

    items_list = list(items)[:limit]
    # Use simple, clean chip rendering
    chip_html = '<div style="display:flex;flex-wrap:wrap;gap:6px;margin:8px 0;">'
    for item in items_list:
        chip_html += f'<span style="background:rgba(124,92,252,0.2);border:1px solid rgba(124,92,252,0.35);padding:5px 10px;border-radius:16px;font-size:12px;font-weight:600;color:#D9E0E7;white-space:nowrap;">{item}</span>'
    chip_html += '</div>'
    st.markdown(chip_html, unsafe_allow_html=True)

def card_start(title: str):
    """Legacy function - use st.container(border=True) instead."""
    st.markdown(f'<div class="card"><h3 style="margin:0 0 10px 0;">{title}</h3>', unsafe_allow_html=True)

def card_end():
    """Legacy function - use st.container(border=True) instead."""
    st.markdown("</div>", unsafe_allow_html=True)

def softline():
    """Render a subtle gradient divider line."""
    st.markdown('<div class="softline"></div>', unsafe_allow_html=True)
