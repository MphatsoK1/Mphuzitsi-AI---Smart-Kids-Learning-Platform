import re
import joblib
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression

training_data = [
    ("hello", "greeting"),
    ("hi there", "greeting"),
    ("hey", "greeting"),
    ("trace letter a", "trace"),
    ("i want to learn b", "trace"),
    ("goodbye", "goodbye"),
    ("bye", "goodbye"),
    ("thank you", "gratitude"),
]

X_train = [x[0] for x in training_data]
y_train = [x[1] for x in training_data]

vectorizer = CountVectorizer()
X_vec = vectorizer.fit_transform(X_train)

model = LogisticRegression()
model.fit(X_vec, y_train)

joblib.dump(model, "models/intent_model.pkl")
joblib.dump(vectorizer, "models/vectorizer.pkl")

def predict_intent(user_text):
    model = joblib.load("models/intent_model.pkl")
    vectorizer = joblib.load("models/vectorizer.pkl")
    X_input = vectorizer.transform([user_text])
    prediction = model.predict(X_input)[0]
    return prediction
