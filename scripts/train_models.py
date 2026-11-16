from pathlib import Path
import joblib
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, log_loss

DATA = Path("data/synthetic_training_data.csv")
OUT = Path("models")
OUT.mkdir(exist_ok=True)
if not DATA.exists():
    raise SystemExit("Run python scripts/generate_training_data.py first.")
df = pd.read_csv(DATA)
features = ["base_ctr","base_cvr","mobile","fr","context_match","user_clicks","user_impressions"]
X = df[features]
models = {}
for name, target in [("ctr","click"), ("cvr","conversion")]:
    # For this toy demo CVR is trained against all rows; production CVR should
    # define the eligible clicked population and handle delayed/mature labels.
    y = df[target]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    model = LogisticRegression(max_iter=500, class_weight=None)
    model.fit(X_train, y_train)
    pred = model.predict_proba(X_test)[:,1]
    print(f"{name.upper()} AUC={roc_auc_score(y_test,pred):.4f} "
          f"LogLoss={log_loss(y_test,pred):.4f}")
    joblib.dump(model, OUT / f"{name}_model.joblib")
print("Saved CTR and CVR models to models/")
