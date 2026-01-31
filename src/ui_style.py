import streamlit as st

def inject_css():
    st.markdown(
        """
        <style>
          /* global spacing + responsive */
          .block-container { 
            padding-top: 1.5rem; 
            padding-bottom: 2.5rem; 
            max-width: 1400px !important;
            width: 100% !important;
            margin: 0 auto !important;
          }
          
          /* mobile responsive */
          @media (max-width: 768px) {
            .block-container {
              padding-left: 0.5rem !important;
              padding-right: 0.5rem !important;
              padding-top: 0.75rem !important;
            }
            h1, h2, h3 { font-size: 1.1rem !important; }
          }
          
          h1, h2, h3, h4, h5, h6 { 
            letter-spacing: -0.01em;
            font-weight: 700;
            line-height: 1.25;
          }
          
          h2 { margin-top: 0.8rem; margin-bottom: 0.8rem; font-size: 1.5rem; }
          h3 { margin-top: 0.6rem; margin-bottom: 0.6rem; font-size: 1.25rem; }
          
          /* input styling */
          .stTextArea textarea { 
            border-radius: 14px !important;
            background: rgba(11,16,32,0.8) !important;
            border: 1px solid rgba(124,92,252,0.2) !important;
            color: rgba(255,255,255,0.95) !important;
            padding: 12px 14px !important;
            font-size: 14px !important;
          }
          .stTextArea textarea:focus { 
            border-color: rgba(124,92,252,0.6) !important;
            box-shadow: 0 0 0 3px rgba(124,92,252,0.1) !important;
          }
          
          .stFileUploader {
            border-radius: 14px !important;
          }
          .stFileUploader [data-testid="stFileUploadDropzone"] {
            border: 2px dashed rgba(124,92,252,0.3) !important;
            border-radius: 14px !important;
            background: rgba(124,92,252,0.05) !important;
            padding: 24px !important;
          }

          /* hide streamlit chrome */
          header, footer { visibility: hidden; }
          #MainMenu { visibility: hidden; }

          /* brand bar */
          .brandbar {
            display:flex; justify-content:space-between; align-items:center;
            background: linear-gradient(135deg, rgba(124,92,252,0.15), rgba(124,92,252,0.08));
            border: 1.5px solid rgba(124,92,252,0.3);
            padding: 16px 20px;
            border-radius: 20px;
            margin-bottom: 20px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.3);
            flex-wrap: wrap;
            gap: 10px;
          }
          
          @media (max-width: 640px) {
            .brandbar {
              padding: 12px 16px;
              margin-bottom: 16px;
            }
          }
          
          .brand-left { display:flex; align-items:center; gap:14px; }
          .logo {
            width: 40px; height: 40px;
            border-radius: 14px;
            background: linear-gradient(135deg, rgba(124,92,252,0.3), rgba(124,92,252,0.15));
            border: 1.5px solid rgba(124,92,252,0.4);
            display:flex; align-items:center; justify-content:center;
            font-weight:800;
            font-size: 18px;
            flex-shrink: 0;
          }
          .title { font-size: 18px; font-weight: 800; margin:0; letter-spacing: -0.01em; }
          .subtitle { font-size: 12px; opacity: 0.75; margin:0; letter-spacing: -0.005em; }

          /* responsive columns */
          .stColumn {
            flex-grow: 1;
            min-width: 0;
          }

          /* button styling */
          .stButton > button {
            border-radius: 12px !important;
            padding: 10px 24px !important;
            font-weight: 700 !important;
            letter-spacing: -0.005em !important;
            border: 1.5px solid rgba(124,92,252,0.3) !important;
            background: linear-gradient(135deg, rgba(124,92,252,0.25), rgba(124,92,252,0.15)) !important;
            color: rgba(255,255,255,0.95) !important;
            transition: all 0.2s ease !important;
            width: 100% !important;
          }
          .stButton > button:hover {
            border-color: rgba(124,92,252,0.6) !important;
            background: linear-gradient(135deg, rgba(124,92,252,0.4), rgba(124,92,252,0.25)) !important;
            box-shadow: 0 4px 12px rgba(124,92,252,0.2) !important;
            transform: translateY(-2px) !important;
          }

          /* selectbox styling */
          .stSelectbox [data-baseweb="select"] {
            border-radius: 12px !important;
          }

          /* status pill */
          .pill {
            display:inline-flex;
            align-items:center;
            justify-content:center;
            gap:8px;
            padding: 7px 12px;
            border-radius: 999px;
            font-size: 12px;
            font-weight: 800;
            border: 1.5px solid rgba(255,255,255,0.15);
            letter-spacing: -0.005em;
            white-space: nowrap;
            min-width: 92px;
          }
          .pill.shortlist { 
            background: rgba(46, 204, 113, 0.18); 
            color: #C8FFD6; 
            border-color: rgba(46,204,113,0.4);
          }
          .pill.review    { 
            background: rgba(241, 196, 15, 0.18); 
            color: #FFFAB2; 
            border-color: rgba(241,196,15,0.35);
          }
          .pill.reject    { 
            background: rgba(231, 76, 60, 0.18); 
            color: #FFCAC2; 
            border-color: rgba(231,76,60,0.35);
          }

          /* divider */
          .softline { 
            height:1px; 
            background: linear-gradient(90deg, rgba(255,255,255,0), rgba(124,92,252,0.2), rgba(255,255,255,0));
            margin: 16px 0; 
          }

          /* tab styling */
          .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            border-bottom: 1px solid rgba(255,255,255,0.06);
            overflow-x: auto;
          }
          .stTabs [aria-selected="true"] {
            border-bottom: 2px solid rgba(124,92,252,0.8) !important;
            color: rgba(124,92,252,0.95) !important;
          }

          /* dataframe styling */
          .stDataFrame {
            border-radius: 12px !important;
            width: 100% !important;
          }
          .stDataFrame [data-testid="stDataFrameContainer"] {
            background: rgba(11,16,32,0.5) !important;
            border: 1px solid rgba(255,255,255,0.05) !important;
            border-radius: 12px !important;
            overflow-x: auto;
          }

          /* metric styling */
          [data-testid="metric-container"] {
            background: transparent !important;
            border: none !important;
            padding: 0.5rem 0.25rem !important;
          }
          [data-testid="metric-container"] > div:first-child {
            font-size: 13px !important;
            opacity: 0.8 !important;
          }
          [data-testid="metric-container"] > div:last-child {
            font-size: 28px !important;
            font-weight: 800 !important;
            letter-spacing: -0.02em !important;
          }

          @media (max-width: 768px) {
            [data-testid="metric-container"] > div:last-child {
              font-size: 22px !important;
            }
          }

        </style>
        """,
        unsafe_allow_html=True,
    )


