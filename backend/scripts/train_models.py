"""
Train, cross-validate, evaluate, and persist the SkillSight AI job-role model:
- Model A: Job-Role Classifier (LinearSVC with CalibratedClassifierCV & LogisticRegression)
- TF-IDF Vectorizer fitted strictly on training data
- Persists model artifacts to backend/artifacts/
- Evaluates test set metrics (Accuracy, Macro-F1, Weighted-F1, Precision, Recall)
"""

import json
import os
import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    classification_report,
    confusion_matrix
)

RANDOM_SEED = 42

def train_job_role_models():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    data_path = os.path.join(base_dir, "data", "synthetic", "synthetic_resumes.csv")
    artifacts_dir = os.path.join(base_dir, "artifacts")
    os.makedirs(artifacts_dir, exist_ok=True)
    
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Synthetic resumes dataset not found at {data_path}. Please run generate_synthetic_data.py first.")
        
    print(f"[1/6] Loading synthetic resumes from {data_path}...")
    df = pd.read_csv(data_path)
    print(f"Loaded {len(df)} records across {df['target_role'].nunique()} roles.")
    
    # Text input and label
    X = df["resume_text"].values
    y = df["target_role"].values
    
    # Stratified train/test split (80% train, 20% test)
    print("[2/6] Performing stratified train/test split (80/20)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_SEED, stratify=y
    )
    
    # Fit TF-IDF Vectorizer ONLY on training set to prevent data leakage
    print("[3/6] Fitting TF-IDF Vectorizer on training data...")
    vectorizer = TfidfVectorizer(
        max_features=5000,
        ngram_range=(1, 2),
        sublinear_tf=True,
        stop_words="english",
        min_df=2
    )
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)
    
    # 5-fold Stratified Cross-Validation on Training Data for Model Selection
    print("[4/6] Evaluating candidate models with 5-Fold Stratified Cross-Validation on training data...")
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_SEED)
    
    lr_candidate = LogisticRegression(max_iter=1000, random_state=RANDOM_SEED, C=1.0)
    lr_cv_scores = cross_val_score(lr_candidate, X_train_vec, y_train, cv=cv, scoring="f1_macro", n_jobs=-1)
    print(f"  Logistic Regression CV Macro-F1: {lr_cv_scores.mean():.4f} (+/- {lr_cv_scores.std():.4f})")
    
    svc_candidate = LinearSVC(random_state=RANDOM_SEED, C=1.0, dual=False)
    svc_cv_scores = cross_val_score(svc_candidate, X_train_vec, y_train, cv=cv, scoring="f1_macro", n_jobs=-1)
    print(f"  LinearSVC CV Macro-F1: {svc_cv_scores.mean():.4f} (+/- {svc_cv_scores.std():.4f})")
    
    # Train Calibrated LinearSVC (to provide well-calibrated probabilities for multi-class ranking)
    print("[5/6] Training calibrated model on full training set...")
    base_svc = LinearSVC(random_state=RANDOM_SEED, C=1.0, dual=False)
    calibrated_model = CalibratedClassifierCV(estimator=base_svc, cv=3)
    calibrated_model.fit(X_train_vec, y_train)
    
    # Also train standard Logistic Regression for comparison
    lr_model = LogisticRegression(max_iter=1000, random_state=RANDOM_SEED, C=1.0)
    lr_model.fit(X_train_vec, y_train)
    
    # Evaluate on held-out test set
    print("[6/6] Evaluating on held-out test set (unseen data)...")
    y_pred_calibrated = calibrated_model.predict(X_test_vec)
    y_pred_lr = lr_model.predict(X_test_vec)
    
    test_acc_cal = accuracy_score(y_test, y_pred_calibrated)
    test_macro_f1_cal = f1_score(y_test, y_pred_calibrated, average="macro")
    test_weighted_f1_cal = f1_score(y_test, y_pred_calibrated, average="weighted")
    test_precision_cal = precision_score(y_test, y_pred_calibrated, average="macro")
    test_recall_cal = recall_score(y_test, y_pred_calibrated, average="macro")
    
    print(f"\n================ TEST SET PERFORMANCE ================")
    print(f"Selected Model: Calibrated LinearSVC")
    print(f"Test Accuracy:         {test_acc_cal * 100:.2f}%")
    print(f"Test Macro-F1:         {test_macro_f1_cal:.4f}")
    print(f"Test Weighted-F1:      {test_weighted_f1_cal:.4f}")
    print(f"Test Precision (Macro): {test_precision_cal:.4f}")
    print(f"Test Recall (Macro):    {test_recall_cal:.4f}")
    print("======================================================")
    
    classes_list = list(calibrated_model.classes_)
    report_dict = classification_report(y_test, y_pred_calibrated, target_names=classes_list, output_dict=True)
    cm = confusion_matrix(y_test, y_pred_calibrated, labels=classes_list).tolist()
    
    # Save artifacts
    model_path = os.path.join(artifacts_dir, "job_role_classifier.joblib")
    vectorizer_path = os.path.join(artifacts_dir, "tfidf_vectorizer.joblib")
    metrics_path = os.path.join(artifacts_dir, "metrics.json")
    
    joblib.dump(calibrated_model, model_path)
    joblib.dump(vectorizer, vectorizer_path)
    
    metrics_data = {
        "model_name": "Calibrated LinearSVC (with TF-IDF)",
        "vectorizer_features": 5000,
        "training_samples": len(X_train),
        "test_samples": len(X_test),
        "accuracy": round(float(test_acc_cal), 4),
        "macro_f1": round(float(test_macro_f1_cal), 4),
        "weighted_f1": round(float(test_weighted_f1_cal), 4),
        "precision_macro": round(float(test_precision_cal), 4),
        "recall_macro": round(float(test_recall_cal), 4),
        "cross_val_mean_macro_f1": round(float(svc_cv_scores.mean()), 4),
        "cross_val_std": round(float(svc_cv_scores.std()), 4),
        "classes": classes_list,
        "per_class_metrics": {c: report_dict[c] for c in classes_list if c in report_dict},
        "confusion_matrix": cm,
    }
    
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics_data, f, indent=2)
        
    print(f"\nArtifacts saved successfully:")
    print(f"  - Model: {model_path}")
    print(f"  - Vectorizer: {vectorizer_path}")
    print(f"  - Metrics: {metrics_path}")

if __name__ == "__main__":
    train_job_role_models()
