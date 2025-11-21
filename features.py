import re
import joblib
import numpy as np
import tldextract
from textblob import TextBlob
import matplotlib.pyplot as plt
import pandas as pd


# Load ML Models

url_model = joblib.load("models/url_model.pkl")        # RandomForest model
email_model = joblib.load("models/email_model.pkl")    # Logistic Regression model
email_tfidf = joblib.load("models/email_tfidf.pkl")    # TF-IDF vectorizer



# URL Heuristic Feature Extraction
# NOTE: Your URL dataset is numeric, but your runtime input is raw text.
# So we re-create numeric features from the URL using heuristics.

def analyze_url(url):
    features = {}
    
    features["index"] = 0     # required to match training dataset columns(First error fixed)

    # 1. IP-based URL
    ip_pattern = r"(\d{1,3}\.){3}\d{1,3}"
    features['having_IPhaving_IP_Address'] = 1 if re.search(ip_pattern, url) else 0

    # 2. URL Length
    url_length = len(url)
    features['URLURL_Length'] = 1 if url_length >= 54 else 0

    # 3. Shortening service
    shortening_patterns = ["bit.ly", "tinyurl", "goo.gl", "t.co", "ow.ly"]
    features['Shortining_Service'] = 1 if any(s in url for s in shortening_patterns) else 0

    # 4. @ symbol
    features['having_At_Symbol'] = 1 if "@" in url else 0

    # 5. //
    features['double_slash_redirecting'] = 1 if url.count("//") > 1 else 0

    # 6. Prefix/Suffix (-)
    domain = tldextract.extract(url).domain
    features['Prefix_Suffix'] = 1 if "-" in domain else 0

    # 7. Subdomain count
    subdomain = tldextract.extract(url).subdomain
    sub_cnt = subdomain.count(".") + 1 if subdomain else 0
    features['having_Sub_Domain'] = 1 if sub_cnt >= 2 else 0

    # 8. HTTPS token
    features['HTTPS_token'] = 1 if "https" in url.lower() else 0

    # Fill missing columns with 0 (to match training dataset)
    all_cols = [
        'index','having_IPhaving_IP_Address','URLURL_Length','Shortining_Service',
        'having_At_Symbol','double_slash_redirecting','Prefix_Suffix','having_Sub_Domain',
        'SSLfinal_State','Domain_registeration_length','Favicon','port','HTTPS_token',
        'Request_URL','URL_of_Anchor','Links_in_tags','SFH','Submitting_to_email',
        'Abnormal_URL','Redirect','on_mouseover','RightClick','popUpWidnow','Iframe',
        'age_of_domain','DNSRecord','web_traffic','Page_Rank','Google_Index',
        'Links_pointing_to_page','Statistical_report'
    ]

    for col in all_cols:
        if col not in features:
            features[col] = 0

    # 9. Statistical report — simple heuristic
    suspicious_keywords = ["login", "secure", "verify", "update", "bank"]
    features['Statistical_report'] = 1 if any(w in url.lower() for w in suspicious_keywords) else 0

    # NOTE:
    # All other dataset fields are website-based (favicon, iframe, DNSRecord...),
    # which cannot be computed from only the URL string at runtime.
    # So we set them to safe defaults (0).
    static_columns = [
        'SSLfinal_State', 'Domain_registeration_length', 'Favicon', 'port', 'Request_URL',
        'URL_of_Anchor', 'Links_in_tags', 'SFH', 'Submitting_to_email', 'Abnormal_URL',
        'Redirect', 'on_mouseover', 'RightClick', 'popUpWidnow', 'Iframe', 'age_of_domain',
        'DNSRecord', 'web_traffic', 'Page_Rank', 'Google_Index',
        'Links_pointing_to_page'
    ]

    for col in static_columns:
        features[col] = 0

    return features



# Email Feature Extraction (Heuristics)

def analyze_email(text):
    features = {}
    clean = text.lower()

    urgency = ['urgent', 'immediately', 'suspended', 'verify', 'alert']
    phishing_words = ['password', 'bank', 'click', 'confirm', 'update']

    features['urgent_words'] = any(w in clean for w in urgency)
    features['phishing_words'] = any(w in clean for w in phishing_words)

    features['exclamation_count'] = clean.count("!")
    features['contains_html'] = 1 if re.search(r"<[^>]+>", text) else 0
    features['link_count'] = len(re.findall(r"http[s]?://\S+", text))
    features['sentiment'] = TextBlob(text).sentiment.polarity
    features['word_count'] = len(clean.split())

    return features



# ML Prediction Functions

def predict_url_ml(features_dict):
    # Exact column order from training dataset
    column_order = [
        'index',
        'having_IPhaving_IP_Address',
        'URLURL_Length',
        'Shortining_Service',
        'having_At_Symbol',
        'double_slash_redirecting',
        'Prefix_Suffix',
        'having_Sub_Domain',
        'SSLfinal_State',
        'Domain_registeration_length',
        'Favicon',
        'port',
        'HTTPS_token',
        'Request_URL',
        'URL_of_Anchor',
        'Links_in_tags',
        'SFH',
        'Submitting_to_email',
        'Abnormal_URL',
        'Redirect',
        'on_mouseover',
        'RightClick',
        'popUpWidnow',
        'Iframe',
        'age_of_domain',
        'DNSRecord',
        'web_traffic',
        'Page_Rank',
        'Google_Index',
        'Links_pointing_to_page',
        'Statistical_report'
    ]

    # Ensure missing fields default to 0
    fixed_features = {col: features_dict.get(col, 0) for col in column_order}

    df = pd.DataFrame([fixed_features], columns=column_order)

    # Predict probability
    prob = url_model.predict_proba(df)[0][1]
    return prob


def predict_email_ml(text):
    vector = email_tfidf.transform([text])
    prob = email_model.predict_proba(vector)[0][1]
    return prob



# Hybrid Scoring

def calculate_score(features, ml_prob):
    h_score = 0

    # Heuristic scoring logic
    if features.get('urgent_words'): h_score += 20
    if features.get('phishing_words'): h_score += 20
    if features.get('exclamation_count', 0) > 2: h_score += 10
    if features.get('contains_html'): h_score += 15
    if features.get('link_count', 0) > 2: h_score += 10
    if features.get('sentiment', 0) < -0.3: h_score += 10

    h_score = min(h_score, 100)

    final_score = (0.6 * ml_prob * 100) + (0.4 * h_score)
    final_score = min(final_score, 100)

    if final_score < 30:
        verdict = "Safe"
    elif final_score < 60:
        verdict = "Suspicious"
    else:
        verdict = "Dangerous"

    return final_score, verdict



# Visualization

def visualize_result(features, score, verdict):
    keys = list(features.keys())
    vals = [int(v) if isinstance(v, bool) else v for v in features.values()]

    plt.figure(figsize=(8, 6))
    plt.barh(keys, vals, color="skyblue")
    plt.title(f"PhishShield Risk Analysis\nScore: {round(score,2)}% | Verdict: {verdict}")
    plt.tight_layout()
    plt.savefig("screenshots/risk_chart.png")
    plt.close()
