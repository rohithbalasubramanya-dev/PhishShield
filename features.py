import re
import tldextract

def analyze_url(url):
    """
    Extract structuralnad lexical features from a url
    (Suspicious words, IP-based URL, domain analysis, etc.)

    """
    features={}
     # 1. check if url is IP based instead of domain
    ip_pattern = r'(\d{1,3}\.){3}\d{1,3}'
    features['ip_based'] = bool(re.search(ip_pattern, url))

     # 2. Extract domain and subdomain using tldextract
    extracted = tldextract.extract(url)
    domain = extracted.domain
    subdomain = extracted.subdomain
    suffix = extracted.suffix

    features['domain'] = domain
    features['subdomain'] = subdomain
    features['suffix'] = suffix

    # 3. Count number of dots
    features['num_dots'] = url.count('.')

    # 4. Suspicious keywords in URL
    suspicious_words = ['login', 'verify', 'update', 'secure', 'banking', 'account']
    features['suspicious_words'] = any(word in url.lower() for word in suspicious_words)

    # 5. Too many hyphens (-) could indicate fake domains
    features['num_hyphens'] = url.count('-')

    # 6. URL length (long URLs are often suspicious)
    features['url_length'] = len(url)

    # 7. Encoded characters (phishers use %20, %3D, etc.)
    features['encoded_chars'] = '%' in url

    # 8. HTTPS or not
    features['https'] = url.startswith("https://")

    # 9. Number of subdomains (ex: login.paypal.com)
    features['subdomain_count'] = len(subdomain.split('.')) if subdomain else 0


    return features

def analyze_email(text):
    """
    extract lingusitic and sentiment based features from email text.
    (Like urgency words, sentiment score, link count and stuff)

    """
    features = {}
    return features

def calculate_score(features):
    """
    compute phishing probability scorebased on the extracted features
    """
    score = 0
    verdict = "Pending"
    return score, verdict

def visualize_result(features, score, verdict):
    """
    Generate visual graph and save it under screenshots/.
    """
    pass