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
    import re
from textblob import TextBlob

def analyze_email(text):
    """
    Extract linguistic, sentiment, and structure-based features from email text.
    Returns a dictionary of detected features.
    """

    features = {}

    # 1. Lowercase the text for easier processing
    clean_text = text.lower()

    # 2. Urgent / Threatening keywords
    urgency_words = ['urgent', 'immediately', 'suspended', 'verify', 
                     'alert', 'warning', 'limited time', 'account locked']
    features['urgent_words'] = any(word in clean_text for word in urgency_words)

    # 3. Phishing intent keywords
    phishing_words = ['password', 'bank', 'update', 'security', 'click here', 
                      'confirm', 'reset', 'unlock']
    features['phishing_words'] = any(word in clean_text for word in phishing_words)

    # 4. check no of links inside the email
    url_regex = r'(http[s]?://[^\s]+)'
    features['link_count'] = len(re.findall(url_regex, text))

    # 5. Sentiment polarity (negative/threatening emails are often phishing)
    sentiment = TextBlob(text).sentiment.polarity
    features['sentiment'] = sentiment

    # 6. checking if HTML content is present
    html_regex = r'<[^>]+>'
    features['contains_html'] = bool(re.search(html_regex, text))

    # 7. Excessive punctuation (like !!!)
    features['exclamation_count'] = clean_text.count('!')

    # 8. Suspicious sender spoof (if "from:" exists)
    spoof_regex = r'from:\s.*@(?!gmail\.com|yahoo\.com|outlook\.com)'
    features['possible_spoof'] = bool(re.search(spoof_regex, clean_text))

    # 9. Word count (short emails with high urgency → suspicious)
    features['word_count'] = len(clean_text.split())

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