"""Запуск эксперимента для нечётного варианта лабораторной работы 5."""
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from decision_tree import DecisionTree
from metrics import binary_metrics, classification_curves

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "output"
SEED = 42
FEATURES = [
    "student_age", "sex", "high_school_type", "scholarship_type",
    "additional_work", "artistic_sports_activity", "partner", "salary",
    "transportation", "accommodation", "mother_education", "father_education",
    "siblings", "parental_status", "mother_occupation", "father_occupation",
    "weekly_study_hours", "reading_non_scientific", "reading_scientific",
    "seminar_attendance", "project_impact", "class_attendance",
    "exam_preparation_company", "exam_preparation_time", "taking_notes",
    "listening", "discussion", "flipped_classroom", "previous_gpa",
    "expected_gpa", "course_id",
]


def prepare_data(path):
    raw = pd.read_csv(path, dtype=str)
    expected = ["STUDENT ID"] + [str(i) for i in range(1, 31)] + ["COURSE ID", "GRADE"]
    if list(raw.columns) != expected or raw.empty:
        raise ValueError("Unexpected UCI 856 schema or empty data.")
    grade = pd.to_numeric(raw["GRADE"], errors="raise")
    if grade.isna().any() or not grade.isin(range(8)).all():
        raise ValueError("GRADE must contain integer categories 0..7.")
    X = raw.drop(columns=["STUDENT ID", "GRADE"]).copy()
    X.columns = FEATURES
    X = X.apply(lambda col: col.str.strip()).replace({"": pd.NA, "?": pd.NA})
    missing = X.isna().sum()
    X = X.fillna("<MISSING>")  # Пропуск становится обычной отдельной категорией.
    return raw, X, (grade >= 3).astype(int).to_numpy(), missing


def main():
    path = ROOT / "data" / "students.csv"
    raw, X, y, missing = prepare_data(path)
    # Один отбор для всей модели. Отдельный генератор не зависит от работы split.
    selected = np.random.default_rng(SEED).choice(X.columns, int(np.sqrt(X.shape[1])), replace=False).tolist()
    X = X[selected]
    train, test = train_test_split(np.arange(len(y)), test_size=0.2,
                                   random_state=SEED, stratify=y)
    model = DecisionTree().fit(X.iloc[train], y[train])
    OUT.mkdir(exist_ok=True)
    (OUT / "tree.txt").write_text(model.text(), encoding="utf-8")
    (OUT / "tree_preview.txt").write_text(model.text(max_depth=3), encoding="utf-8")
    leaf_probs = [node.probability for node, _ in model.nodes() if not node.children]
    rows, areas = [], {}
    for name, indices in (("train", train), ("test", test)):
        scores = model.predict_proba(X.iloc[indices])
        prediction = (scores >= 0.5).astype(int)
        rows.append({"split": name, **binary_metrics(y[indices], prediction)})
        pd.DataFrame({"row": indices, "student_id": raw.iloc[indices]["STUDENT ID"].to_numpy(),
                      "y": y[indices], "score": scores, "prediction": prediction}).to_csv(
                          OUT / f"{name}_predictions.csv", index=False)
        if name == "test":
            curve, areas = classification_curves(y[indices], scores, leaf_probs)
            curve.to_csv(OUT / "threshold_curves.csv", index=False)
    metrics = pd.DataFrame(rows)
    metrics.to_csv(OUT / "metrics.csv", index=False)
    importance = pd.DataFrame({"feature": selected, "sum_IG": [model.importances[f] for f in selected]})
    importance = importance.sort_values("sum_IG", ascending=False, kind="stable")
    importance.to_csv(OUT / "feature_importance.csv", index=False)
    split = pd.DataFrame({"row": np.arange(len(y)), "split": "train", "y": y})
    split.loc[test, "split"] = "test"
    split.to_csv(OUT / "split.csv", index=False)
    missing.rename("missing_count").to_csv(OUT / "missing_values.csv", index_label="feature")
    counts = {name: {str(c): int(np.sum(y[indices] == c)) for c in (0, 1)}
              for name, indices in (("all", np.arange(len(y))), ("train", train), ("test", test))}
    summary = {"seed": SEED, "variant": "odd", "source": "https://archive.ics.uci.edu/dataset/856",
               "dataset_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
               "objects": len(y), "candidate_features": len(FEATURES), "selected_features": selected,
               "missing_values": int(missing.sum()), "raw_duplicate_rows": int(raw.duplicated().sum()),
               "class_counts": counts, "tree": model.statistics(), "metrics": rows,
               "test_auc": areas, "leaf_probabilities": sorted(set(leaf_probs)),
               "node_features": sorted({n.feature for n, _ in model.nodes() if n.feature}),
               "threshold_rule": "score >= threshold", "importance_rule": "unweighted sum of node IG"}
    (OUT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    from graphics import plot_results
    plot_results(OUT, counts, importance, curve, areas)
    print("Selected features:", selected)
    print("Class counts:", counts)
    print("Tree:", summary["tree"])
    print(metrics.to_string(index=False))
    print("Test AUC:", areas)
    print(model.text(max_depth=3))


if __name__ == "__main__":
    main()
