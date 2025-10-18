# app.py
from fastapi import FastAPI, UploadFile, File
from clo_analytics_service2 import load_course_data, load_grades_csv, compute_clo
import pandas as pd
import os
import io

app = FastAPI()

@app.post("/process_clo")
async def process_clo(course_code: str, file: UploadFile = File(...)):
    """Receive a cleaned CSV from Blazor, run CLO analytics, and return table."""
    try:
        import tempfile, os

        # 1️⃣ Get system temp directory (cross-platform)
        tmp_dir = tempfile.gettempdir()

        # 2️⃣ Sanitize filename (just use base name, no slashes)
        filename = os.path.basename(file.filename).replace("\\", "_").replace("/", "_")

        # 3️⃣ Build valid path
        temp_path = os.path.join(tmp_dir, filename)
        print(f"Saving uploaded file to: {temp_path}")

        # 4️⃣ Write file content
        contents = await file.read()
        with open(temp_path, "wb") as f:
            f.write(contents)

        # 5️⃣ Proceed with analysis
        clo_df, assessments = load_course_data(course_code)
        df = load_grades_csv(temp_path, list(assessments.keys()))
        result = compute_clo(df, clo_df, assessments)

        # 6️⃣ Clean up
        try: os.remove(temp_path)
        except: pass

        return result.to_dict(orient="records")

    except Exception as e:
        return {"error": str(e)}
