import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import joblib
import os

def train():
    print("Loading dataset...")
    df = pd.read_csv('expense_dataset.csv')

    # Features (X) and Labels (y)
    X = df['description']
    y = df['category']

    print("Step 1: Converting text to numbers using TF-IDF Vectorizer...")
    # TF-IDF converts words into a matrix of numbers based on their frequency and importance
    vectorizer = TfidfVectorizer()
    X_vectorized = vectorizer.fit_transform(X)

    print("Step 2: Training the Logistic Regression model...")
    # Logistic Regression learns the mathematical relationship between the TF-IDF numbers and the categories
    classifier = LogisticRegression(max_iter=1000)
    classifier.fit(X_vectorized, y)

    print("Step 3: Saving the trained model...")
    os.makedirs('model', exist_ok=True)
    
    # joblib saves our trained Python objects to files so Flask can load them later
    joblib.dump(vectorizer, 'model/vectorizer.pkl')
    joblib.dump(classifier, 'model/classifier.pkl')

    print("\nSuccess! Model trained and saved in the 'model/' directory.")
    print("You can now run 'python app.py' to start the application.")

if __name__ == "__main__":
    train()
