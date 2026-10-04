import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report

# 1. Load dataset
df = pd.read_csv(r"C:\Users\abine\Downloads\phishing_dataset.csv")

# 2. Combine textual features into a rich text representation for TF-IDF
# Adjust column names if your dataset uses 'email_body', 'text', or 'subject'
text_cols = [col for col in ['email_category', 'device_type', 'email_client', 'spoofed_domain'] if col in df.columns]

if text_cols:
    df['combined_text'] = df[text_cols].astype(str).agg(' '.join, axis=1)
    X = df['combined_text']
else:
    # Fallback if a single text body column exists
    X = df.iloc[:, 0].astype(str)

# 3. Clean target labels
y = df['label']
if y.dtype == 'object':
    y = y.map({'Legitimate': 0, 'Safe': 0, 'Phishing': 1}).fillna(0)

# 4. Split dataset 80/20[span_1](start_span)[span_1](end_span)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 5. Vectorize text with TF-IDF[span_2](start_span)[span_2](end_span)
vectorizer = TfidfVectorizer(max_features=5000)
X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

# 6. Train Random Forest model[span_3](start_span)[span_3](end_span)
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train_vec, y_train)

# 7. Evaluate model
y_pred = clf.predict(X_test_vec)
print("Classification Report:\n", classification_report(y_test, y_pred))

# 8. Save model and vectorizer[span_4](start_span)[span_4](end_span)
joblib.dump(vectorizer, "tfidf_vectorizer.pkl")
joblib.dump(clf, "phishing_model.pkl")
print("Model and vectorizer saved successfully!")