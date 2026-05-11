# ResumeIQ

ResumeIQ is a lightweight semantic AI resume screening and candidate ranking
system for recruiters. It helps a recruiter create job requirements, upload
resumes, extract resume content, compare candidates with a job description, rank
the applicants, shortlist or reject candidates, and view recruiter-focused
analytics.

The project is built to be locally executable, academically explainable, and
simple enough to understand module by module.

## Features

- Recruiter/admin registration and login
- Create, view, expand, and delete job requirements
- Multiple resume upload for PDF and DOCX files
- Local resume storage in `uploads/`
- PDF parsing with `pdfplumber`
- DOCX parsing with `python-docx`
- Email and phone extraction
- Candidate name cleanup
- Resume section extraction for experience and projects
- Text preprocessing with NLTK
- Skill extraction using keyword dictionaries and regex
- Semantic embeddings with Sentence Transformers
- `all-MiniLM-L6-v2` sentence embedding model
- Cosine similarity matching
- Match percentage calculation
- Skill overlap and missing skill detection
- Experience relevance score
- Project relevance score
- Resume completeness score
- Weighted candidate ranking
- Shortlist and reject actions
- Download shortlisted candidates as a PDF report
- Analytics dashboard generated from uploaded resumes
- Chart.js charts for score, skill, domain, and status analytics
- 100 generated visual PDF resumes for testing and presentation

## Tech Stack

Frontend:

- Flask templates
- TailwindCSS CDN
- Minimal JavaScript
- Chart.js

Backend:

- Flask
- SQLite

Resume parsing:

- `pdfplumber`
- `python-docx`

NLP and semantic AI:

- NLTK
- Sentence Transformers
- `all-MiniLM-L6-v2`
- cosine similarity

Utilities:

- NumPy
- pandas
- scikit-learn
- reportlab for shortlisted candidate PDF reports

## Project Structure

```text
resumeiq/
├── app.py
├── README.md
├── PRESENTATION_INPUTS.md
├── requirements.txt
├── semantic_test.py
│
├── ai/
│   ├── analytics.py
│   ├── embeddings.py
│   ├── matcher.py
│   └── ranking.py
│
├── automated_tests/
│   ├── README.md
│   ├── compare_network_modes.py
│   ├── run_full_pipeline_check.py
│   ├── sample_case_outputs.py
│   ├── test_full_pipeline_fast.py
│   └── test_modules.py
│
├── database/
│   ├── .gitkeep
│   └── database.db
│
├── models/
│   └── .gitkeep
│
├── scripts/
│   ├── create_resume_templates.py
│   ├── create_synthetic_visual_pdf_resumes.py
│   └── create_visual_resume_templates.py
│
├── static/
│   ├── charts/
│   ├── css/
│   └── js/
│       └── dashboard.js
│
├── synthetic_visual_resumes_pdf/
│   └── 100 generated PDF resumes
│
├── templates/
│   ├── _messages.html
│   ├── dashboard.html
│   ├── login.html
│   └── register.html
│
├── uploads/
│   └── .gitkeep
│
└── utils/
    ├── database.py
    ├── parser.py
    ├── preprocess.py
    ├── scoring.py
    └── skills.py
```

## Application Flow

1. Recruiter registers or logs in.
2. Recruiter creates a job requirement.
3. Recruiter uploads multiple resumes.
4. ResumeIQ parses PDF or DOCX content.
5. ResumeIQ extracts email, phone, skills, experience, and project sections.
6. Text is preprocessed with NLTK.
7. Resume and job text are converted into semantic embeddings.
8. Cosine similarity produces semantic relevance scores.
9. Skill overlap and missing skills are calculated.
10. Candidate scores are combined into a weighted final match percentage.
11. Candidates are ranked in the dashboard.
12. Recruiter shortlists or rejects candidates.
13. Analytics cards and charts update from uploaded resume data.
14. Recruiter can download a PDF report of shortlisted candidates.

## Scoring Logic

ResumeIQ ranks candidates with a readable weighted formula:

```text
final_score =
    semantic_similarity * 0.40
  + skill_match         * 0.35
  + experience_score    * 0.15
  + project_score       * 0.10
```

The final score is displayed as a recruiter-friendly percentage.

Other dashboard metrics include:

- average match score
- average semantic score
- average skill match
- top detected skill
- most missing skill
- average resume completeness
- experience relevance
- project relevance
- candidate match score distribution
- semantic relevance distribution
- top detected skills chart
- domain distribution chart
- shortlisted vs rejected chart
- AI insight panel

## First-Time Setup Notes

The first setup requires internet access to install Python packages and download
the Sentence Transformer model and NLTK resources. After these are cached on the
machine, the backend matching and tests can run locally from the cache.

The dashboard currently loads TailwindCSS and Chart.js from CDNs in the browser,
so the cleanest visual dashboard experience needs internet access unless those
browser assets are already cached.

## Setup on macOS

### 1. Install Homebrew

Open Terminal and run:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

After installation, follow any Homebrew instructions printed in the terminal.
On Apple Silicon Macs, Homebrew usually asks you to add it to your shell path.

Common Apple Silicon path setup:

```bash
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"
```

Common Intel Mac path setup:

```bash
echo 'eval "$(/usr/local/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/usr/local/bin/brew shellenv)"
```

Check Homebrew:

```bash
brew --version
```

### 2. Install Python

```bash
brew install python
```

Check Python and pip:

```bash
python3 --version
python3 -m pip --version
```

### 3. Open the project

```bash
cd "/Users/sathvik/RS Codex/resumeiq"
```

If your project is in a different folder, replace the path with your local
project path.

### 4. Create a virtual environment

```bash
python3 -m venv venv
```

### 5. Activate the virtual environment

```bash
source venv/bin/activate
```

Your terminal should now show `(venv)`.

### 6. Upgrade pip

```bash
python -m pip install --upgrade pip
```

### 7. Install dependencies

```bash
pip install -r requirements.txt
```

### 8. Start the app

```bash
python app.py
```

Open this URL in a browser:

```text
http://127.0.0.1:5001
```

### 9. Stop the app

Press:

```text
Control + C
```

## Setup on Linux

These steps use Ubuntu/Debian commands. For Fedora, Arch, or another Linux
distribution, install Python 3, pip, and venv using that distribution's package
manager.

### 1. Update packages

```bash
sudo apt update
```

### 2. Install Python, pip, and venv

```bash
sudo apt install python3 python3-pip python3-venv
```

### 3. Check Python and pip

```bash
python3 --version
python3 -m pip --version
```

### 4. Open the project

```bash
cd /path/to/resumeiq
```

Replace `/path/to/resumeiq` with your actual project folder.

### 5. Create a virtual environment

```bash
python3 -m venv venv
```

### 6. Activate the virtual environment

```bash
source venv/bin/activate
```

### 7. Upgrade pip

```bash
python -m pip install --upgrade pip
```

### 8. Install dependencies

```bash
pip install -r requirements.txt
```

### 9. Start the app

```bash
python app.py
```

Open:

```text
http://127.0.0.1:5001
```

### 10. Stop the app

Press:

```text
Ctrl + C
```

## Setup on Windows

### 1. Install Python

1. Go to `https://www.python.org/downloads/`.
2. Download the latest stable Python 3 installer for Windows.
3. Run the installer.
4. Very important: check `Add python.exe to PATH`.
5. Click `Install Now`.

### 2. Open PowerShell

Open PowerShell from the Start menu.

### 3. Check Python and pip

```powershell
py --version
py -m pip --version
```

If `py` does not work, try:

```powershell
python --version
python -m pip --version
```

### 4. Open the project

Example:

```powershell
cd "C:\Users\YourName\Downloads\resumeiq"
```

Use your actual project path.

### 5. Create a virtual environment

```powershell
py -m venv venv
```

If `py` does not work:

```powershell
python -m venv venv
```

### 6. Activate the virtual environment

```powershell
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then activate again:

```powershell
.\venv\Scripts\Activate.ps1
```

### 7. Upgrade pip

```powershell
python -m pip install --upgrade pip
```

### 8. Install dependencies

```powershell
pip install -r requirements.txt
```

### 9. Start the app

```powershell
python app.py
```

Open:

```text
http://127.0.0.1:5001
```

### 10. Stop the app

Press:

```text
Ctrl + C
```

## NLTK Resources

The app checks for these NLTK resources:

- `punkt`
- `punkt_tab`
- `stopwords`
- `wordnet`
- `omw-1.4`

They are downloaded automatically when preprocessing needs them. To download
them manually, run this inside the activated virtual environment:

```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab'); nltk.download('stopwords'); nltk.download('wordnet'); nltk.download('omw-1.4')"
```

Use the same command in PowerShell on Windows.

## First Run

1. Start the app.
2. Open `http://127.0.0.1:5001`.
3. Register a recruiter account.
4. Log in.
5. Create a job requirement.
6. Upload PDF or DOCX resumes.
7. Review ranking, analytics, skill gaps, and AI insights.
8. Shortlist or reject candidates.
9. Download the shortlisted candidate PDF report if needed.

## Demo Resumes

The generated visual PDF resumes are in:

```text
synthetic_visual_resumes_pdf/
```

There are 100 generated PDF resumes covering multiple domains:

- backend development
- frontend development
- full stack engineering
- data analytics
- data science
- machine learning
- NLP
- DevOps
- cloud engineering
- cybersecurity
- database administration
- mobile development
- UI/UX
- graphic design
- digital marketing
- HR
- business analysis
- project management
- product management
- finance
- sales
- customer support
- content writing
- QA
- operations

For presentation-ready job descriptions, required skills, PDF upload lists, and
expected outputs, use:

```text
PRESENTATION_INPUTS.md
```

Recommended presentation order:

1. Backend API Hiring
2. Data Science Analytics Hiring
3. DevOps Cloud Hiring
4. Frontend Product UI Hiring
5. Business Product Operations Hiring
6. QA Automation Hiring

## Running Automated Tests

Activate the virtual environment first.

macOS/Linux:

```bash
source venv/bin/activate
```

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

Run module tests:

```bash
python -m unittest discover automated_tests -p "test_*.py"
```

Run the full offline 100-resume pipeline check:

```bash
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 python automated_tests/run_full_pipeline_check.py --mode offline
```

On Windows PowerShell:

```powershell
$env:HF_HUB_OFFLINE="1"
$env:TRANSFORMERS_OFFLINE="1"
python automated_tests/run_full_pipeline_check.py --mode offline
Remove-Item Env:\HF_HUB_OFFLINE
Remove-Item Env:\TRANSFORMERS_OFFLINE
```

Compare offline and normal cached execution:

```bash
python automated_tests/compare_network_modes.py
```

## Semantic Similarity Test

Run:

```bash
python semantic_test.py
```

Expected behavior:

- `Built REST APIs using FastAPI`
- `Backend API development`

should score higher than:

- `Graphic design using Photoshop`

This demonstrates semantic matching rather than simple keyword matching.

## Database

SQLite is used for local storage.

Database file:

```text
database/database.db
```

Main tables:

- `users`
- `jobs`
- `resumes`
- `candidates`

To reset local app data during testing, stop the Flask server and delete:

```text
database/database.db
```

The app will recreate the database tables on the next run.

## Uploads

Uploaded resumes are stored in:

```text
uploads/
```

The folder contains `.gitkeep` so the directory exists in Git. Uploaded files
are local runtime data and do not need to be committed.

## Common Commands

Start app:

```bash
python app.py
```

Run unit tests:

```bash
python -m unittest discover automated_tests -p "test_*.py"
```

Run full pipeline test:

```bash
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 python automated_tests/run_full_pipeline_check.py --mode offline
```

Deactivate virtual environment:

```bash
deactivate
```

## Troubleshooting

### `python` command not found

Use:

```bash
python3 --version
python3 app.py
```

On Windows, use:

```powershell
py --version
py app.py
```

### `pip` command not found

Use:

```bash
python -m pip install -r requirements.txt
```

or:

```bash
python3 -m pip install -r requirements.txt
```

### Port 5001 is already in use

Another copy of the app may already be running. Stop the old terminal process
with `Ctrl + C`.

On macOS/Linux, you can check:

```bash
lsof -nP -iTCP:5001 -sTCP:LISTEN
```

### Sentence Transformer model download is slow

The first run may take time because the model is downloaded and cached. Later
runs reuse the local cache.

### Charts or styling look plain

TailwindCSS and Chart.js are loaded from CDNs. Make sure the browser has
internet access for the best dashboard visuals.

## Notes for Presenters

- Create a fresh job for each demo case.
- Upload only the PDFs listed for that case.
- Do not mix multiple demo cases into the same job unless you intentionally want
  combined analytics.
- Scores can vary slightly if the job description text is changed.
- The important behavior to demonstrate is that relevant resumes rank higher,
  missing skills are detected, and analytics update from uploaded resumes.
