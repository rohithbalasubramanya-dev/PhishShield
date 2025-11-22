import re
import joblib
import numpy as np
import tldextract
from textblob import TextBlob
import matplotlib.pyplot as plt
import pandas as pd

# ============================================
# LOAD EMAIL ML MODEL + TF-IDF
# ============================================
email_model = joblib.load("models/email_model.pkl")
email_tfidf = joblib.load("models/email_tfidf.pkl")


# ============================================
# URL HEURISTIC ANALYSIS (NO ML)
# ============================================
def analyze_url(url):
    features = {}

    # Important: dataset had index column
    features['index'] = 0

    # 1. IP-based URL
    ip_pattern = r"(\d{1,3}\.){3}\d{1,3}"
    features['having_IPhaving_IP_Address'] = 1 if re.search(ip_pattern, url) else 0

    # 2. URL length
    features['URLURL_Length'] = 1 if len(url) >= 54 else 0

    # 3. Shortening service
    shortening_services = ["bit.ly", "tinyurl", "goo.gl", "t.co", "ow.ly"]
    features['Shortining_Service'] = 1 if any(s in url for s in shortening_services) else 0

    # 4. @ symbol usage → very suspicious
    features['having_At_Symbol'] = 1 if "@" in url else 0

    # 5. // redirecting
    features['double_slash_redirecting'] = 1 if url.count("//") > 1 else 0

    # 6. Prefix-Suffix using "-"
    domain = tldextract.extract(url).domain
    features['Prefix_Suffix'] = 1 if "-" in domain else 0

    # 7. Subdomain count
    sub = tldextract.extract(url).subdomain
    sub_count = sub.count(".") + 1 if sub else 0
    features['having_Sub_Domain'] = 1 if sub_count >= 2 else 0

    # 8. HTTPS token
    features['HTTPS_token'] = 1 if "https" in url.lower() else 0

    # 9. Statistical patterns (common phishing keywords)
    keywords = ["secure", "login", "verify", "account", "update", "bank"]
    features['Statistical_report'] = 1 if any(k in url.lower() for k in keywords) else 0

    # === Other dataset columns not usable from URL string → set to 0 ===
    static_cols = [
        'SSLfinal_State', 'Domain_registeration_length', 'Favicon', 'port',
        'Request_URL', 'URL_of_Anchor', 'Links_in_tags', 'SFH', 'Submitting_to_email',
        'Abnormal_URL', 'Redirect', 'on_mouseover', 'RightClick', 'popUpWidnow',
        'Iframe', 'age_of_domain', 'DNSRecord', 'web_traffic', 'Page_Rank',
        'Google_Index', 'Links_pointing_to_page'
    ]

    for col in static_cols:
        features[col] = 0

    return features


# ============================================
# EMAIL HEURISTIC ANALYSIS
# ============================================
def analyze_email(text):
    features = {}
    text_low = text.lower()

    urgency_words = ['urgent', 'immediately', 'suspended', 'verify', 'alert']
    phishing_words = ['password', 'bank', 'click', 'confirm', 'update']

    features['urgent_words'] = any(w in text_low for w in urgency_words)
    features['phishing_words'] = any(w in text_low for w in phishing_words)

    features['exclamation_count'] = text_low.count("!")
    features['contains_html'] = 1 if re.search(r"<[^>]+>", text) else 0
    features['link_count'] = len(re.findall(r"http[s]?://\S+", text))
    features['sentiment'] = TextBlob(text).sentiment.polarity
    features['word_count'] = len(text_low.split())

    return features


# ============================================
# EMAIL ML PREDICTION
# ============================================
def predict_email_ml(text):
    vector = email_tfidf.transform([text])
    prob = email_model.predict_proba(vector)[0][1]
    return prob


# ============================================
# HYBRID SCORING LOGIC
# ============================================
def calculate_score(features, ml_prob, input_type):
    h_score = 0

    if input_type == "url":
        # Pure Heuristic Scoring (NO ML)
        if features['having_IPhaving_IP_Address']: h_score += 30
        if features['URLURL_Length']: h_score += 5
        if features['Shortining_Service']: h_score += 20
        if features['having_At_Symbol']: h_score += 10
        if features['double_slash_redirecting']: h_score += 15
        if features['Prefix_Suffix']: h_score += 15
        if features['having_Sub_Domain']: h_score += 20
        if not features['HTTPS_token']: h_score += 30
        if features['Statistical_report']: h_score += 10

        final_score = h_score

    else:
        # EMAIL = ML + heuristics
        if features['urgent_words']: h_score += 20
        if features['phishing_words']: h_score += 25
        if features['exclamation_count'] > 2: h_score += 15
        if features['contains_html']: h_score += 20
        if features['link_count'] > 2: h_score += 15
        if features['sentiment'] < -0.3: h_score += 35

        h_score = min(h_score, 100)
        final_score = (0.8 * ml_prob * 100) - (0.2 * h_score)

    # Verdict
    if final_score < 30:
        verdict = "Safe"
    elif final_score < 60:
        verdict = "Suspicious"
    else:
        verdict = "Dangerous"

    return final_score, verdict


# ============================================
# VISUALISATION
# ============================================
def visualize_result(features, score, verdict):
    labels = list(features.keys())
    values = [int(v) if isinstance(v, bool) else v for v in features.values()]

    plt.figure(figsize=(9, 6))
    plt.barh(labels, values, color="orange")
    plt.title(f"PhishShield Risk Analysis\nScore: {round(score,2)} | Verdict: {verdict}")
    plt.tight_layout()
    plt.savefig("screenshots/risk_chart.png")
    plt.close()
