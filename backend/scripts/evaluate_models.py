"""Evaluate saved job-role model artifacts against synthetic resume data."""

import os
import json
import joblib
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, classification_report

def evaluate():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    model_path = os.path.join(base_dir, "artifacts", "job_role_classifier.joblib")
    vec_path = os.path.join(base_dir, "artifacts", "tfidf_vectorizer.joblib")
    data_path = os.path.join(base_dir, "data", "synthetic", "synthetic_resumes.csv")
    
    if not os.path.exists(model_path) or not os.path.exists(vec_path):
        print("[ERROR] Model artifacts not found. Please run train_models.py first.")
        return
        
    print("[1/3] Loading model and vectorizer artifacts...")
    model = joblib.load(model_path)
    vectorizer = joblib.load(vec_path)
    
    print("[2/3] Loading test samples...")
    df = pd.read_csv(data_path)
    # Take sample of 500 for quick validation
    sample_df = df.sample(n=min(500, len(df)), random_state=123)
    
    X_vec = vectorizer.transform(sample_df["resume_text"].values)
    y_true = sample_df["target_role"].values
    
    print("[3/3] Generating predictions...")
    y_pred = model.predict(X_vec)
    
    acc = accuracy_score(y_true, y_pred)
    macro_f1 = f1_score(y_true, y_pred, average="macro")
    
    print(f"\nModel Evaluation Result:")
    print(f"Sample Accuracy: {acc * 100:.2f}%")
    print(f"Sample Macro-F1: {macro_f1:.4f}")
    print("\nDetailed Per-Class Report:")
    print(classification_report(y_true, y_pred))

if __name__ == "__main__":
    evaluate()
