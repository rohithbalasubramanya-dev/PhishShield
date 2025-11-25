import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import time

# ============================================
# 1. PAGE CONFIGURATION & STYLING
# ============================================
st.set_page_config(
    page_title="PhishShield V1.0",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- ULTIMATE CYBER CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;700&family=Share+Tech+Mono&display=swap');

    /* 1. BACKGROUND - DEEP VOID */
    .stApp {
        background-color: #000000;
        background-image: 
            radial-gradient(circle at 50% 50%, #0a1a0a 0%, #000000 100%);
        color: #00ff41;
    }

    /* 2. DYNAMIC CARDS (The "Pop & Glow" Effect) */
    .cyber-card {
        background: rgba(10, 20, 10, 0.6);
        border: 1px solid #00ff41;
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 0 10px rgba(0, 255, 65, 0.1);
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        margin-bottom: 20px;
        text-align: center;
    }
    
    .cyber-card:hover {
        transform: translateY(-5px) scale(1.02); /* POP UP EFFECT */
        box-shadow: 0 0 30px rgba(0, 255, 65, 0.5), inset 0 0 20px rgba(0, 255, 65, 0.1); /* NEON GLOW */
        border-color: #fff;
        z-index: 10;
    }

    /* 3. FIXING THE CHARTS TO GLOW */
    /* This applies the glow effect directly to the chart containers */
    .stPlotlyChart {
        background: rgba(5, 15, 5, 0.8);
        border: 1px solid #333;
        border-radius: 10px;
        padding: 10px;
        transition: all 0.3s ease;
    }
    .stPlotlyChart:hover {
        border-color: #00ff41;
        box-shadow: 0 0 25px rgba(0, 255, 65, 0.4);
        transform: scale(1.02);
    }

    /* 4. INPUT BOX - BREATHING ANIMATION */
    @keyframes breathe {
        0% { border-color: #004400; box-shadow: 0 0 5px rgba(0,255,65,0.1); }
        50% { border-color: #00ff41; box-shadow: 0 0 20px rgba(0,255,65,0.4); }
        100% { border-color: #004400; box-shadow: 0 0 5px rgba(0,255,65,0.1); }
    }

    .stTextArea textarea {
        background-color: #020502 !important;
        color: #00ff41 !important;
        font-family: 'Share Tech Mono', monospace;
        font-size: 16px;
        border: 2px solid #004400 !important;
        border-radius: 5px;
        animation: breathe 3s infinite; /* Breathing effect */
    }
    .stTextArea textarea:focus {
        animation: none;
        border-color: #00ff41 !important;
        box-shadow: 0 0 30px rgba(0, 255, 65, 0.6);
    }

    /* 5. THE SCAN BUTTON */
    .stButton > button {
        width: 100%;
        background: #000;
        color: #00ff41;
        border: 2px solid #00ff41;
        font-family: 'Rajdhani', sans-serif;
        font-size: 24px;
        font-weight: bold;
        text-transform: uppercase;
        padding: 20px;
        letter-spacing: 3px;
        transition: 0.2s;
        box-shadow: 0 0 10px rgba(0, 255, 65, 0.2);
    }
    .stButton > button:hover {
        background: #00ff41;
        color: #000;
        box-shadow: 0 0 40px rgba(0, 255, 65, 0.8);
        transform: scale(1.05);
    }

    /* 6. TYPOGRAPHY */
    h1 {
        font-family: 'Rajdhani', sans-serif;
        font-size: 4rem;
        text-transform: uppercase;
        text-align: center;
        text-shadow: 0 0 20px rgba(0, 255, 65, 0.8);
        margin-bottom: 0;
    }
    .subtitle {
        font-family: 'Share Tech Mono', monospace;
        text-align: center;
        color: #888;
        font-size: 1.2rem;
        letter-spacing: 2px;
        margin-bottom: 40px;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# ============================================
# 2. LOAD ENGINE
# ============================================
try:
    import features
    MODELS_LOADED = True
except Exception:
    MODELS_LOADED = False

# ============================================
# 3. HIGH-VISIBILITY CHART FUNCTIONS
# ============================================

def clean_name(name):
    """Cybersecurity Jargon Mapper"""
    mapping = {
        'having_IPhaving_IP_Address': 'HOST_IDENTITY_IP',
        'URLURL_Length': 'STRING_LENGTH_ANOMALY',
        'Shortining_Service': 'OBFUSCATION_SERVICE',
        'having_At_Symbol': 'EMBEDDED_CREDENTIALS',
        'double_slash_redirecting': 'OPEN_REDIRECT_DETECTED',
        'Prefix_Suffix': 'DOMAIN_SPOOFING_ATTEMPT',
        'having_Sub_Domain': 'SUBDOMAIN_DEPTH_OVERFLOW',
        'HTTPS_token': 'ENCRYPTION_LAYER_MISSING',
        'Statistical_report': 'THREAT_INTEL_MATCH',
        'urgent_words': 'COERCIVE_LANGUAGE_PATTERN',
        'phishing_words': 'CREDENTIAL_HARVESTING_TERMS',
        'contains_html': 'MALICIOUS_HTML_PAYLOAD',
        'link_count': 'OUTBOUND_LINK_FLOOD',
        'exclamation_count': 'SENTIMENT_ANOMALY'
    }
    return mapping.get(name, name.upper())

def create_risk_gauge(score):
    """Massive, High-Contrast Gauge"""
    if score < 30: 
        color = "#00ff41" # Neon Green
    elif score < 60: 
        color = "#ffb300" # Neon Orange
    else: 
        color = "#ff0000" # Neon Red

    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "THREAT PROBABILITY", 'font': {'size': 24, 'color': "white", 'family': "Rajdhani"}},
        number = {'suffix': "%", 'font': {'color': color, 'size': 60, 'family': "Share Tech Mono"}},
        gauge = {
            'axis': {'range': [None, 100], 'tickwidth': 2, 'tickcolor': "white"},
            'bar': {'color': color, 'thickness': 1}, # Thick bar
            'bgcolor': "rgba(0,0,0,0.5)",
            'borderwidth': 2,
            'bordercolor': "#fff",
            'steps': [],
        }
    ))
    # Transparent background so it glows against the page
    fig.update_layout(paper_bgcolor = "rgba(0,0,0,0)", font = {'color': "white"}, height=350, margin=dict(l=30, r=30, t=50, b=30))
    return fig

def create_radar(feat):
    """Attack Vector Triangulation Radar"""
    categories = ['URL Structure', 'Domain Reputation', 'Content Analysis', 'Social Eng (Urgency)', 'Tech Anomalies']
    
    # Weights for visual impact
    v_url = sum([feat.get('URLURL_Length',0), feat.get('double_slash_redirecting',0), feat.get('Shortining_Service',0)]) * 25
    v_domain = sum([feat.get('having_IPhaving_IP_Address',0), feat.get('having_Sub_Domain',0), feat.get('Prefix_Suffix',0)]) * 25
    v_content = sum([feat.get('phishing_words',0), feat.get('Statistical_report',0)]) * 40
    v_urgency = sum([feat.get('urgent_words',0), 1 if feat.get('exclamation_count',0)>1 else 0]) * 50
    v_tech = sum([feat.get('contains_html',0), 1 if feat.get('HTTPS_token',0)==0 else 0]) * 50 
    
    values = [min(v, 100) for v in [v_url, v_domain, v_content, v_urgency, v_tech]]
    
    fig = go.Figure(data=go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        fillcolor='rgba(0, 255, 65, 0.3)',
        line=dict(color='#00ff41', width=3),
        marker=dict(size=8, color="white")
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], showticklabels=False, linecolor='#555'),
            angularaxis=dict(tickfont=dict(size=12, color="#ccc", family="Rajdhani")),
            bgcolor='rgba(0,0,0,0.5)'
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        title=dict(text="ATTACK VECTOR TRIANGULATION", font=dict(size=20, color="white", family="Rajdhani")),
        height=350,
        margin=dict(l=40, r=40, t=50, b=40)
    )
    return fig

# ============================================
# 4. MAIN INTERFACE
# ============================================

# --- HERO HEADER ---
st.markdown("<h1>PHISH<span style='color:#00ff41'>SHIELD</span> <span style='font-size:2rem'>V1.0</span></h1>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>// ADVANCED ML-POWERED THREAT INTELLIGENCE GRID //</div>", unsafe_allow_html=True)

# --- CENTERED INPUT MODULE ---
c1, c2, c3 = st.columns([1, 2, 1])

with c2:
    input_text = st.text_area("Input", height=100, placeholder=">> PASTE SUSPICIOUS URL OR EMAIL HEADER HERE...", label_visibility="collapsed")
    
    # Spacing for button
    st.markdown("<br>", unsafe_allow_html=True)
    
    analyze = st.button("INITIATE NEURAL SCAN")

# --- ANALYSIS RESULTS ---
if analyze:
    if not input_text:
        st.warning("⚠️ INPUT STREAM EMPTY. PLEASE PROVIDE DATA.")
    elif not MODELS_LOADED:
        st.error("❌ NEURAL ENGINE OFFLINE. (Model files missing)")
    else:
        # --- LOADING ANIMATION ---
        with st.spinner("⚡ ESTABLISHING SECURE UPLINK... ANALYZING VECTORS..."):
            time.sleep(1.5) # Suspense delay
            
        # --- LOGIC ---
        if "\n" in input_text.strip() or ("http" not in input_text and "www" not in input_text):
            feat = features.analyze_email(input_text)
            ml_prob = features.predict_email_ml(input_text)
            final_score, verdict = features.calculate_score(feat, ml_prob, "email")
        else:
            feat = features.analyze_url(input_text)
            ml_prob = 0.0
            final_score, verdict = features.calculate_score(feat, ml_prob, "url")
            
        st.markdown("---")
        
        # --- LAYOUT GRID ---
        # Three large columns for the main stats
        col_stat, col_gauge, col_radar = st.columns([1, 1, 1])
        
        # 1. VERDICT CARD
        if verdict == "Dangerous":
            main_color = "#ff0000" # Red
            icon = "💀"
            sub_msg = "CRITICAL THREAT DETECTED"
        elif verdict == "Suspicious":
            main_color = "#ffb300" # Orange
            icon = "☢️"
            sub_msg = "HIGH RISK ANOMALY"
        else:
            main_color = "#00ff41" # Green
            icon = "🛡️"
            sub_msg = "TARGET SECURE"
            
        with col_stat:
            # HTML Card with Hover Effect CSS class 'cyber-card'
            st.markdown(f"""
            <div class="cyber-card" style="border-color: {main_color}; height: 370px; display: flex; flex-direction: column; justify-content: center;">
                <div style="font-size: 80px; margin-bottom: 10px; text-shadow: 0 0 20px {main_color};">{icon}</div>
                <h2 style="color: {main_color}; font-size: 3.5rem; margin: 0; text-shadow: 0 0 10px {main_color};">{verdict.upper()}</h2>
                <div style="font-family: 'Share Tech Mono'; color: #fff; margin-top: 15px; letter-spacing: 2px; font-size: 1.2rem;">
                    {sub_msg}
                </div>
                <div style="margin-top: 20px; border: 1px solid {main_color}; padding: 5px; color: {main_color}; font-weight: bold; display: inline-block;">
                    CONFIDENCE: {round(ml_prob*100, 1)}%
                </div>
            </div>
            """, unsafe_allow_html=True)

        # 2. GAUGE CHART (Using Native Plotly Container)
        with col_gauge:
            # We don't wrap this in HTML. We let Streamlit render it, and our global CSS handles the glow.
            st.plotly_chart(create_risk_gauge(final_score), use_container_width=True)

        # 3. RADAR CHART (Using Native Plotly Container)
        with col_radar:
            st.plotly_chart(create_radar(feat), use_container_width=True)

        # --- DETAILED FORENSICS SECTION ---
        st.markdown("<br><h2 style='text-align: center; color: #fff;'>🔬 FORENSIC LOG ANALYSIS</h2>", unsafe_allow_html=True)
        
        cols = st.columns(4)
        idx = 0
        
        for k, v in feat.items():
            if k in ['index', 'word_count', 'sentiment', 'Statistical_report']: continue
            
            # LOGIC: Detect if this feature is a threat
            is_active_threat = False
            
            # HTTPS Logic: 0 means missing (BAD)
            if k == 'HTTPS_token':
                if v == 0: is_active_threat = True
            # Normal Logic: 1 or True means present (BAD)
            else:
                if isinstance(v, bool) and v: is_active_threat = True
                elif isinstance(v, int) and v > 0: is_active_threat = True
            
            if is_active_threat:
                clean_n = clean_name(k)
                with cols[idx % 4]:
                    st.markdown(f"""
                    <div class="cyber-card" style="border-color: #ff0000; padding: 10px; min-height: 100px; display: flex; align-items: center; justify-content: center; flex-direction: column;">
                        <div style="color: #ff0000; font-weight: bold; font-family: 'Share Tech Mono'; font-size: 1.2rem;">⚠ DETECTED</div>
                        <div style="color: #ccc; font-size: 0.9rem; margin-top: 5px;">{clean_n}</div>
                    </div>
                    """, unsafe_allow_html=True)
                idx += 1
        
        if idx == 0:
            st.success("✅ SYSTEM SCAN COMPLETE: NO ANOMALIES DETECTED. TARGET IS CLEAN.")