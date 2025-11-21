import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os
import re

print("Loading Email dataset...")

# Load data
df = pd.read_csv("data/phishing_emails.csv")

# Convert text labels → integers
df['Email Type'] = df['Email Type'].map({
    "Phishing Email": 1,
    "Safe Email": 0
})

# Drop rows with missing/invalid labels
df = df.dropna(subset=['Email Type'])

# ============================
# EMAIL CLEANING FUNCTION
# ============================
def clean_email(text):
    text = str(text)

    # Remove HTML tags
    text = re.sub(r'<[^>]+>', ' ', text)
    # Remove links
    text = re.sub(r'http[s]?://\S+', ' ', text)
    # Remove symbols
    text = re.sub(r'[^A-Za-z ]+', ' ', text)

    return text.lower().strip()

# Apply cleaning
df['clean_text'] = df['Email Text'].apply(clean_email)

X = df['clean_text']
y = df['Email Type'].astype(int)

# ============================
# TRAIN/TEST SPLIT
# ============================
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# ============================
# TF-IDF VECTORIZER
# ============================
tfidf = TfidfVectorizer(max_features=50000, stop_words='english')

X_train_vec = tfidf.fit_transform(X_train)
X_test_vec = tfidf.transform(X_test)

# ============================
# MACHINE LEARNING MODEL
# ============================
model = LogisticRegression(max_iter=2000)
model.fit(X_train_vec, y_train)

# ============================
# EVALUATION
# ============================
preds = model.predict(X_test_vec)
acc = accuracy_score(y_test, preds)

print("\nEmail Model Accuracy:", acc)
print("\nClassification Report:")
print(classification_report(y_test, preds))

# ============================
# SAVE MODEL + TF-IDF
# ============================
os.makedirs("models", exist_ok=True)

joblib.dump(model, "models/email_model.pkl")
joblib.dump(tfidf, "models/email_tfidf.pkl")

print("\nModel saved to models/ folder.")
