from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from clo_analytics_service2 import load_course_data, load_grades_csv, compute_clo
import tempfile
import os

app = FastAPI()

# -----------------------------
# Allow Blazor & local access
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Root route
# -----------------------------
from fastapi import FastAPI, UploadFile, File, Form

@app.post("/process_clo")
async def process_clo(course_code: str = Form(...), file: UploadFile = File(...)):


# -----------------------------
# CLO Analytics endpoint
# -----------------------------
@app.post("/process_clo")
async def process_clo(course_code: str, file: UploadFile = File(...)):
    try:
        import tempfile, os
        from clo_analytics_service2 import load_course_data, load_grades_csv, compute_clo

        tmp_dir = tempfile.gettempdir()
        filename = os.path.basename(file.filename).replace("\\", "_").replace("/", "_")
        temp_path = os.path.join(tmp_dir, filename)

        contents = await file.read()
        with open(temp_path, "wb") as f:
            f.write(contents)

        clo_df, assessments = load_course_data(course_code)
        df = load_grades_csv(temp_path, list(assessments.keys()))
        result = compute_clo(df, clo_df, assessments)

        os.remove(temp_path)
        return result.to_dict(orient="records")

    except Exception as e:
        return {"error": str(e)}
