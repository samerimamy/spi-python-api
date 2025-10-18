import os
import json
import pandas as pd

# ---------------------------------------------------
# Load Course Configuration from JSON
# ---------------------------------------------------
def load_course_data(course_code):
    """Load the CLO weights and assessment settings from the JSON file."""
    data_dir = os.path.join(os.path.dirname(__file__), "course_data")
    file_path = os.path.join(data_dir, f"{course_code}.json")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"No configuration found for {course_code}")

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    clo_df = pd.DataFrame(data["clo_weights"])
    assessments = data["assessments"]
    print(f"📘 Loaded configuration for {course_code}")
    return clo_df, assessments


# ---------------------------------------------------
# Safe CSV loader that ignores header rows and text lines
# ---------------------------------------------------
def load_grades_csv(csv_path, expected_cols):
    """Load grades safely, ignoring non-numeric header rows."""
    print(f"📂 Reading CSV: {csv_path}")
    df = pd.read_csv(csv_path, header=None, dtype=str)  # read all as text
    df = df.dropna(how="all")  # remove empty rows

    # 1️⃣ Detect non-numeric header row
    def is_non_numeric_row(row):
        non_numeric = 0
        for v in row:
            try:
                float(v)
            except Exception:
                non_numeric += 1
        return non_numeric >= len(row) / 2

    # 2️⃣ Skip the first line if it looks like a header
    if not df.empty and is_non_numeric_row(df.iloc[0]):
        print("🧹 Skipping first line — looks like a header inside data")
        df = df.iloc[1:].reset_index(drop=True)

    # 3️⃣ Convert to numeric where possible
    df = df.apply(pd.to_numeric, errors="coerce")

    # 4️⃣ Keep only the last N columns that match assessments
    df = df.iloc[:, -len(expected_cols):]
    df.columns = expected_cols

    # 5️⃣ Drop rows with no numeric data
    df = df.dropna(how="all").reset_index(drop=True)

    print(f"✅ Cleaned CSV shape: {df.shape}")
    return df


# ---------------------------------------------------
# Main CLO computation logic
# ---------------------------------------------------
def compute_clo(df, clo_df, assessments):
    """Compute weighted CLO achievements."""
    assessment_cols = list(assessments.keys())

    # Compute averages per assessment
    averages = {col: df[col].mean() for col in assessment_cols}
    print("\n📊 Assessment Averages:")
    print(averages)

    # Compute average achievement (%)
    avg_achievement = {k: (v / assessments[k]) * 100 for k, v in averages.items()}
    print("\n🎯 Average Achievement (%):")
    print(avg_achievement)

    # Compute weighted CLO achievements
    results = []
    for _, row in clo_df.iterrows():
        clo = row["CLO"]
        clo_result = {"CLO": clo}
        total = 0

        for col in assessment_cols:
            weighted = (avg_achievement[col] * row[col]) / 100
            clo_result[col] = round(weighted, 2)
            total += weighted

        clo_result["TOTAL"] = round(total, 2)
        clo_result["MET"] = "MET" if total >= 70 else "NOT MET"
        results.append(clo_result)

    return pd.DataFrame(results)


# ---------------------------------------------------
# Example usage (main script)
# ---------------------------------------------------
if __name__ == "__main__":
    course_code = "MISY2313"

    # 1️⃣ Load course configuration
    clo_df, assessments = load_course_data(course_code)

    # 2️⃣ Load CSV safely (ignore headers, clean data)
    csv_path = os.path.join(os.path.dirname(__file__), "api", "cleaned.csv")
    df = load_grades_csv(csv_path, list(assessments.keys()))

    # 3️⃣ Compute CLO achievement
    result = compute_clo(df, clo_df, assessments)

    # 4️⃣ Display results
    print("\n✅ CLO Achievement Matrix:\n")
    print(result.to_string(index=False))
