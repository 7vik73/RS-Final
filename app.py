"""ResumeIQ Flask application.

Run locally with:
    python app.py

The app uses no training pipeline. Every match is calculated dynamically from
uploaded resumes, recruiter job descriptions, extracted skills, and sentence
transformer embeddings.
"""

import json
from pathlib import Path

from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from ai.analytics import chart_data, dashboard_metrics, empty_charts, empty_metrics
from ai.matcher import calculate_relevance_scores
from ai.ranking import calculate_final_score
from utils.database import execute, fetch_all, fetch_one, init_database
from utils.parser import extract_candidate_name, parse_resume, sections_to_json
from utils.preprocess import preprocess_text
from utils.scoring import calculate_resume_strength
from utils.skills import compare_skills, extract_skills, split_required_skills


BASE_DIR = Path(__file__).resolve().parent
UPLOAD_FOLDER = BASE_DIR / "uploads"
ALLOWED_EXTENSIONS = {".pdf", ".docx"}

app = Flask(__name__)
app.secret_key = "resumeiq-local-dev-secret"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024


def allowed_file(filename):
    """Validate resume extension before saving the upload."""
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS


def current_user_id():
    return session.get("user_id")


def login_required(view):
    """Small decorator for the single recruiter/admin user flow."""
    def wrapped_view(*args, **kwargs):
        if not current_user_id():
            flash("Please log in to access ResumeIQ.", "warning")
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    wrapped_view.__name__ = view.__name__
    return wrapped_view


@app.route("/")
def home():
    if current_user_id():
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Username and password are required.", "error")
            return redirect(url_for("register"))

        try:
            execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, generate_password_hash(password)),
            )
        except Exception:
            flash("That username is already registered.", "error")
            return redirect(url_for("register"))

        flash("Account created. Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = fetch_one("SELECT * FROM users WHERE username = ?", (username,))

        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            flash("Welcome back to ResumeIQ.", "success")
            return redirect(url_for("dashboard"))

        flash("Invalid username or password.", "error")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    user_id = current_user_id()
    jobs = fetch_all(
        "SELECT * FROM jobs WHERE user_id = ? ORDER BY created_at DESC",
        (user_id,),
    )
    selected_job_id = request.args.get("job_id") or (jobs[0]["id"] if jobs else None)

    selected_job = None
    candidates = []
    metrics = empty_metrics()
    charts = empty_charts()

    if selected_job_id:
        selected_job = fetch_one(
            "SELECT * FROM jobs WHERE id = ? AND user_id = ?",
            (selected_job_id, user_id),
        )

    if selected_job:
        candidates = get_filtered_candidates(selected_job["id"])
        metrics = dashboard_metrics(selected_job["id"])
        charts = chart_data(selected_job["id"])

    return render_template(
        "dashboard.html",
        jobs=jobs,
        selected_job=selected_job,
        candidates=candidates,
        metrics=metrics,
        charts=json.dumps(charts),
        filters=request.args,
    )


@app.route("/jobs", methods=["POST"])
@login_required
def create_job():
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    required_skills = request.form.get("required_skills", "").strip()

    if not title or not description:
        flash("Job title and description are required.", "error")
        return redirect(url_for("dashboard"))

    job_id = execute(
        """
        INSERT INTO jobs (user_id, title, description, required_skills)
        VALUES (?, ?, ?, ?)
        """,
        (current_user_id(), title, description, required_skills),
    )
    flash("Job requirement created.", "success")
    return redirect(url_for("dashboard", job_id=job_id))


@app.route("/upload/<int:job_id>", methods=["POST"])
@login_required
def upload_resumes(job_id):
    job = fetch_one(
        "SELECT * FROM jobs WHERE id = ? AND user_id = ?",
        (job_id, current_user_id()),
    )
    if not job:
        flash("Create a job requirement before uploading resumes.", "error")
        return redirect(url_for("dashboard"))

    files = request.files.getlist("resumes")
    saved_count = 0

    for file in files:
        if not file or not file.filename:
            continue
        if not allowed_file(file.filename):
            flash(f"Skipped unsupported file: {file.filename}", "warning")
            continue

        filename = secure_filename(file.filename)
        stored_path = unique_upload_path(filename)
        file.save(stored_path)
        analyze_and_store_resume(job, filename, stored_path)
        saved_count += 1

    flash(f"Uploaded and analyzed {saved_count} resume(s).", "success")
    return redirect(url_for("dashboard", job_id=job_id))


@app.route("/candidate/<int:candidate_id>/status", methods=["POST"])
@login_required
def update_candidate_status(candidate_id):
    status = request.form.get("status", "Pending")
    candidate = fetch_one(
        """
        SELECT candidates.*, jobs.user_id
        FROM candidates
        JOIN jobs ON jobs.id = candidates.job_id
        WHERE candidates.id = ?
        """,
        (candidate_id,),
    )

    if not candidate or candidate["user_id"] != current_user_id():
        flash("Candidate not found.", "error")
        return redirect(url_for("dashboard"))

    execute("UPDATE candidates SET status = ? WHERE id = ?", (status, candidate_id))
    flash(f"Candidate marked as {status}.", "success")
    return redirect(url_for("dashboard", job_id=candidate["job_id"]))


def unique_upload_path(filename):
    """Avoid overwriting files when multiple resumes share a filename."""
    UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
    path = UPLOAD_FOLDER / filename
    counter = 1
    while path.exists():
        path = UPLOAD_FOLDER / f"{Path(filename).stem}_{counter}{Path(filename).suffix}"
        counter += 1
    return path


def analyze_and_store_resume(job, filename, stored_path):
    """Parse a resume, extract NLP features, and store its ranking scores."""
    parsed = parse_resume(stored_path)
    cleaned_text = preprocess_text(parsed["raw_text"])
    resume_skills = parsed["skills"]
    required_skills = split_required_skills(job["required_skills"])

    if not required_skills:
        required_skills = extract_skills(job["description"])

    overlap, missing, skill_score = compare_skills(resume_skills, required_skills)
    relevance = calculate_relevance_scores(cleaned_text, job["description"], parsed["sections"])
    strength = calculate_resume_strength(parsed["raw_text"], resume_skills, parsed["sections"])
    final_score = calculate_final_score(
        relevance["semantic_score"],
        skill_score,
        relevance["experience_score"],
        relevance["project_score"],
    )

    resume_id = execute(
        """
        INSERT INTO resumes
            (user_id, job_id, filename, stored_path, raw_text, cleaned_text, email, phone, skills, sections)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            current_user_id(),
            job["id"],
            filename,
            str(stored_path),
            parsed["raw_text"],
            cleaned_text,
            parsed["email"],
            parsed["phone"],
            ", ".join(resume_skills),
            sections_to_json(parsed["sections"]),
        ),
    )

    execute(
        """
        INSERT INTO candidates
            (resume_id, job_id, candidate_name, semantic_score, skill_score,
             experience_score, project_score, resume_strength, final_score,
             overlap_skills, missing_skills)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            resume_id,
            job["id"],
            extract_candidate_name(filename, parsed["raw_text"]),
            relevance["semantic_score"],
            skill_score,
            relevance["experience_score"],
            relevance["project_score"],
            strength,
            final_score,
            ", ".join(overlap),
            ", ".join(missing),
        ),
    )


def get_filtered_candidates(job_id):
    """Apply recruiter filters while keeping SQL simple and readable."""
    min_score = request.args.get("min_score", type=float)
    skill = request.args.get("skill", "").strip().lower()
    status = request.args.get("status", "").strip()

    query = """
        SELECT
            candidates.*,
            resumes.filename,
            resumes.email,
            resumes.phone,
            resumes.skills,
            resumes.raw_text
        FROM candidates
        JOIN resumes ON resumes.id = candidates.resume_id
        WHERE candidates.job_id = ?
    """
    params = [job_id]

    if min_score is not None:
        query += " AND candidates.final_score >= ?"
        params.append(min_score)

    if status:
        query += " AND candidates.status = ?"
        params.append(status)

    if skill:
        query += " AND LOWER(resumes.skills) LIKE ?"
        params.append(f"%{skill}%")

    query += " ORDER BY candidates.final_score DESC"
    return fetch_all(query, params)


if __name__ == "__main__":
    init_database()
    UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
    app.run(debug=True, host="127.0.0.1", port=5001)
