"""Create synthetic visual PDF resumes for ResumeIQ testing.

All people and details in these PDFs are fictional. The files are designed as
sample input data for local resume parsing, semantic matching, ranking, and
analytics tests.
"""

from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    HRFlowable,
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "synthetic_visual_resumes_pdf"
ZIP_PATH = BASE_DIR / "synthetic_visual_resumes_pdf.zip"


FIRST_NAMES = [
    "Aarav", "Maya", "Rohan", "Anika", "Kabir", "Ishita", "Dev", "Nisha", "Arjun", "Meera",
    "Kiran", "Tara", "Vikram", "Priya", "Neel", "Sana", "Aditya", "Riya", "Rahul", "Aisha",
    "Yash", "Kavya", "Nikhil", "Diya", "Samar", "Leela", "Varun", "Ananya", "Ishan", "Pooja",
    "Amit", "Sara", "Jay", "Tanya", "Rehan", "Mina", "Om", "Zoya", "Manav", "Ira",
    "Harsh", "Noor", "Akash", "Rhea", "Siddharth", "Avni", "Krish", "Myra", "Vivaan", "Jiya",
    "Eshan", "Lara", "Parth", "Sia", "Rudra", "Kiara", "Neil", "Mira", "Dhruv", "Reva",
    "Aryan", "Zara", "Tejas", "Aditi", "Rishi", "Nora", "Kunal", "Tisha", "Shaurya", "Ina",
    "Madhav", "Raina", "Arnav", "Lavanya", "Uday", "Samira", "Naveen", "Elina", "Pranav", "Amaya",
    "Rajat", "Tanvi", "Kartik", "Sneha", "Ansh", "Farah", "Mihir", "Ritika", "Vihaan", "Alia",
    "Gaurav", "Naina", "Ayaan", "Megha", "Darsh", "Suhani", "Raghav", "Anvi", "Laksh", "Tia",
]

LAST_NAMES = [
    "Sharma", "Patel", "Rao", "Iyer", "Mehta", "Nair", "Kapoor", "Joshi", "Reddy", "Bose",
    "Malhotra", "Menon", "Chopra", "Gupta", "Pillai", "Khan", "Verma", "Saxena", "Das", "Shetty",
    "Kulkarni", "Bhat", "Sinha", "Mishra", "Agarwal", "Ghosh", "Jain", "Thomas", "Chatterjee", "Roy",
    "Dutta", "Naidu", "Arora", "Bajaj", "Gill", "George", "Kohli", "Banerjee", "Pandey", "Yadav",
    "Singh", "Fernandes", "Desai", "Mathur", "Trivedi", "Bansal", "Mohan", "Kumar", "Sethi", "Varma",
    "Bhandari", "Bhatt", "Grover", "Lal", "Shah", "Prasad", "Raman", "Juneja", "Tandon", "Luthra",
    "Walia", "Vohra", "Suri", "Hegde", "Pai", "Rastogi", "Chawla", "Purohit", "Bora", "Sodhi",
    "Mirza", "Bakshi", "Apte", "Mahajan", "Patil", "Rana", "Dhar", "Chauhan", "Talwar", "Mitra",
    "Nagpal", "Sarin", "Kale", "Ojha", "Rawat", "Bedi", "Saluja", "Lobo", "Sawant", "Thakur",
    "Dixit", "Soman", "Gandhi", "Dugal", "Parikh", "Saha", "Tiwari", "Bora", "Kashyap", "Madan",
]

DOMAINS = [
    ("Backend Python Developer", ["python", "flask", "fastapi", "sqlite", "postgresql", "rest api", "git"], "built scalable APIs and backend services"),
    ("Frontend React Developer", ["javascript", "typescript", "react", "tailwind", "html", "css", "git"], "built responsive user interfaces and component systems"),
    ("Full Stack Engineer", ["python", "javascript", "flask", "react", "sqlite", "api", "git"], "delivered full stack web features from database to UI"),
    ("Data Analyst", ["python", "sql", "excel", "power bi", "tableau", "pandas", "matplotlib"], "turned business data into dashboards and insights"),
    ("Data Scientist", ["python", "machine learning", "nlp", "pandas", "numpy", "scikit-learn", "matplotlib"], "developed predictive analytics and experimentation workflows"),
    ("Machine Learning Engineer", ["python", "machine learning", "deep learning", "pytorch", "tensorflow", "scikit-learn", "docker"], "implemented ML pipelines and model-serving workflows"),
    ("NLP Engineer", ["python", "nlp", "nltk", "transformers", "sentence transformers", "scikit-learn", "api"], "built semantic text processing and search prototypes"),
    ("DevOps Engineer", ["linux", "git", "docker", "kubernetes", "aws", "ci/cd", "monitoring"], "automated deployment, observability, and release pipelines"),
    ("Cloud Engineer", ["aws", "azure", "gcp", "linux", "docker", "terraform", "networking"], "designed cloud infrastructure and migration workflows"),
    ("Cybersecurity Analyst", ["linux", "network security", "siem", "incident response", "python", "risk assessment", "firewalls"], "monitored threats and improved security operations"),
    ("Database Administrator", ["sql", "mysql", "postgresql", "oracle", "backup", "performance tuning", "linux"], "managed reliable databases and query performance"),
    ("Mobile App Developer", ["kotlin", "swift", "flutter", "firebase", "api integration", "git", "mobile ui"], "built mobile features with API integrations"),
    ("UI/UX Designer", ["figma", "wireframes", "prototyping", "user research", "design systems", "usability testing", "accessibility"], "designed usable product flows and prototypes"),
    ("Graphic Designer", ["photoshop", "illustrator", "branding", "layout design", "typography", "figma", "creative assets"], "created visual identities and marketing assets"),
    ("Digital Marketing Specialist", ["seo", "google analytics", "content marketing", "social media", "email marketing", "campaigns", "excel"], "managed performance campaigns and organic growth"),
    ("HR Recruiter", ["recruitment", "screening", "interviewing", "onboarding", "ats", "communication", "excel"], "screened candidates and coordinated hiring workflows"),
    ("Business Analyst", ["requirements gathering", "stakeholder management", "sql", "excel", "jira", "process mapping", "documentation"], "translated stakeholder needs into clear requirements"),
    ("Project Manager", ["agile", "scrum", "jira", "risk management", "planning", "stakeholder communication", "reporting"], "coordinated teams, risks, and delivery plans"),
    ("Product Manager", ["roadmap", "user research", "analytics", "prioritization", "agile", "wireframes", "stakeholders"], "prioritized product improvements using data and user feedback"),
    ("Finance Analyst", ["excel", "financial modeling", "forecasting", "budgeting", "variance analysis", "power bi", "reporting"], "built financial reports and budget forecasts"),
    ("Sales Executive", ["lead generation", "crm", "negotiation", "pipeline management", "communication", "market research", "reporting"], "managed pipelines and converted qualified leads"),
    ("Customer Support Specialist", ["customer service", "ticketing", "communication", "crm", "troubleshooting", "documentation", "sla"], "resolved customer issues and improved support documentation"),
    ("Content Writer", ["copywriting", "seo", "editing", "research", "blog writing", "content strategy", "wordpress"], "created search-friendly content and editorial calendars"),
    ("Quality Assurance Tester", ["manual testing", "automation testing", "selenium", "api testing", "bug reporting", "jira", "test cases"], "tested web products and improved defect tracking"),
    ("Operations Manager", ["process improvement", "vendor management", "excel", "reporting", "team management", "inventory", "planning"], "improved operating processes and team reporting"),
]

DOMAIN_EXTRAS = {
    "Backend Python Developer": ["mysql", "postman", "redis", "django"],
    "Frontend React Developer": ["figma", "bootstrap", "vue", "accessibility"],
    "Full Stack Engineer": ["nodejs", "express", "mysql", "docker"],
    "Data Analyst": ["forecasting", "analytics", "reporting", "google analytics"],
    "Data Scientist": ["transformers", "forecasting", "analytics", "deep learning"],
    "Machine Learning Engineer": ["nlp", "transformers", "api", "linux"],
    "NLP Engineer": ["machine learning", "deep learning", "pandas", "numpy"],
    "DevOps Engineer": ["terraform", "networking", "incident response", "risk assessment"],
    "Cloud Engineer": ["kubernetes", "ci/cd", "monitoring", "risk assessment"],
    "Cybersecurity Analyst": ["monitoring", "networking", "documentation", "incident response"],
    "Database Administrator": ["sqlite", "mongodb", "redis", "backup"],
    "Mobile App Developer": ["react", "typescript", "prototyping", "accessibility"],
    "UI/UX Designer": ["typography", "branding", "layout design", "creative assets"],
    "Graphic Designer": ["wireframes", "prototyping", "design systems", "accessibility"],
    "Digital Marketing Specialist": ["copywriting", "wordpress", "market research", "analytics"],
    "HR Recruiter": ["stakeholder management", "documentation", "reporting", "planning"],
    "Business Analyst": ["analytics", "agile", "scrum", "reporting"],
    "Project Manager": ["process improvement", "documentation", "excel", "analytics"],
    "Product Manager": ["requirements gathering", "jira", "process mapping", "documentation"],
    "Finance Analyst": ["sql", "analytics", "market research", "excel"],
    "Sales Executive": ["customer service", "email marketing", "social media", "excel"],
    "Customer Support Specialist": ["bug reporting", "test cases", "process improvement", "documentation"],
    "Content Writer": ["social media", "email marketing", "google analytics", "figma"],
    "Quality Assurance Tester": ["python", "git", "postman", "manual testing"],
    "Operations Manager": ["risk management", "stakeholder management", "budgeting", "vendor management"],
}

COMPANIES = [
    "NovaEdge Solutions", "BrightPath Labs", "CloudNest Systems", "PixelForge Studio",
    "DataBridge Analytics", "GreenStack Technologies", "NorthStar Digital",
    "BluePeak Consulting", "UrbanGrid Services", "MetricWave Labs",
]

PROJECT_THEMES = [
    "candidate screening workflow", "inventory forecasting dashboard", "customer ticket tracker",
    "API performance monitor", "mobile onboarding flow", "marketing campaign report",
    "security incident log", "finance variance dashboard", "content planning system",
    "cloud migration checklist",
]

CERTIFICATIONS = [
    "Python Application Foundations", "Agile Delivery Essentials", "Data Analytics Practitioner",
    "Cloud Fundamentals", "Security Awareness Professional", "UX Research Basics",
    "Digital Campaign Strategy", "SQL for Business Reporting", "Quality Testing Foundations",
    "Recruitment Operations Certificate",
]

PALETTES = [
    ("#0F766E", "#CCFBF1", "#134E4A"), ("#1D4ED8", "#DBEAFE", "#1E3A8A"),
    ("#7C3AED", "#EDE9FE", "#4C1D95"), ("#C2410C", "#FFEDD5", "#7C2D12"),
    ("#047857", "#D1FAE5", "#064E3B"), ("#BE123C", "#FFE4E6", "#881337"),
    ("#4338CA", "#E0E7FF", "#312E81"), ("#334155", "#E2E8F0", "#0F172A"),
    ("#A16207", "#FEF3C7", "#713F12"), ("#0E7490", "#CFFAFE", "#164E63"),
]

LAYOUTS = ["left_sidebar", "right_sidebar", "top_band", "split_header", "minimal"]


def hex_color(value):
    return colors.HexColor(value)


def styles(accent):
    base = getSampleStyleSheet()
    return {
        "name": ParagraphStyle("Name", parent=base["Title"], fontName="Helvetica-Bold", fontSize=22, leading=26, textColor=hex_color(accent), spaceAfter=2),
        "name_white": ParagraphStyle("NameWhite", parent=base["Title"], fontName="Helvetica-Bold", fontSize=22, leading=26, textColor=colors.white, alignment=TA_CENTER, spaceAfter=2),
        "role": ParagraphStyle("Role", parent=base["Normal"], fontName="Helvetica-Bold", fontSize=10, leading=13, textColor=colors.HexColor("#334155"), spaceAfter=8),
        "role_white": ParagraphStyle("RoleWhite", parent=base["Normal"], fontName="Helvetica-Bold", fontSize=10, leading=13, textColor=colors.white, alignment=TA_CENTER, spaceAfter=4),
        "heading": ParagraphStyle("Heading", parent=base["Heading2"], fontName="Helvetica-Bold", fontSize=10, leading=12, textColor=hex_color(accent), spaceBefore=7, spaceAfter=3),
        "small_heading": ParagraphStyle("SmallHeading", parent=base["Heading3"], fontName="Helvetica-Bold", fontSize=9, leading=11, textColor=hex_color(accent), spaceBefore=6, spaceAfter=2),
        "body": ParagraphStyle("Body", parent=base["Normal"], fontName="Helvetica", fontSize=8.6, leading=11, textColor=colors.HexColor("#111827"), spaceAfter=3),
        "small": ParagraphStyle("Small", parent=base["Normal"], fontName="Helvetica", fontSize=8, leading=10, textColor=colors.HexColor("#334155"), spaceAfter=2),
        "sidebar": ParagraphStyle("Sidebar", parent=base["Normal"], fontName="Helvetica", fontSize=8, leading=10, textColor=colors.HexColor("#111827"), spaceAfter=3),
        "muted": ParagraphStyle("Muted", parent=base["Normal"], fontName="Helvetica", fontSize=7.5, leading=9, textColor=colors.HexColor("#64748B"), spaceAfter=2),
    }


def bullet_list(items, style):
    return ListFlowable(
        [ListItem(Paragraph(item, style), leftIndent=8) for item in items],
        bulletType="bullet",
        start="circle",
        leftIndent=10,
        bulletFontSize=5,
    )


def candidate(index):
    domain = DOMAINS[index % len(DOMAINS)]
    first = FIRST_NAMES[index % len(FIRST_NAMES)]
    last = LAST_NAMES[(index * 7) % len(LAST_NAMES)]
    name = f"{first} {last}"
    email = f"{first.lower()}.{last.lower()}{index + 1}@example.com"
    phone = f"+91 9{800000000 + (index * 13791):09d}"
    city = ["Bengaluru", "Hyderabad", "Pune", "Mumbai", "Delhi", "Chennai", "Kochi", "Ahmedabad"][index % 8]
    years = 1 + (index % 8)
    rotation = (index // len(DOMAINS)) % len(domain[1])
    base_skills = domain[1][rotation:] + domain[1][:rotation]
    extras = DOMAIN_EXTRAS.get(domain[0], [])
    extra_skills = [extras[(index + offset) % len(extras)] for offset in range(min(2, len(extras)))]
    skills = list(dict.fromkeys(base_skills + extra_skills))[:8]
    return {
        "name": name,
        "email": email,
        "phone": phone,
        "city": city,
        "role": domain[0],
        "skills": skills,
        "focus": domain[2],
        "years": years,
        "company": COMPANIES[index % len(COMPANIES)],
        "previous_company": COMPANIES[(index + 3) % len(COMPANIES)],
        "project": PROJECT_THEMES[index % len(PROJECT_THEMES)],
        "certification": CERTIFICATIONS[index % len(CERTIFICATIONS)],
    }


def sidebar_content(data, s, accent):
    return [
        Paragraph("CONTACT", s["small_heading"]),
        Paragraph(data["email"], s["sidebar"]),
        Paragraph(data["phone"], s["sidebar"]),
        Paragraph(f"{data['city']}, India", s["sidebar"]),
        Paragraph("linkedin.com/in/sample-profile", s["sidebar"]),
        Paragraph("CORE SKILLS", s["small_heading"]),
        bullet_list(data["skills"], s["sidebar"]),
        Paragraph("CERTIFICATIONS", s["small_heading"]),
        Paragraph(data["certification"], s["sidebar"]),
        Paragraph(f"{data['role']} Applied Workshop", s["sidebar"]),
        Paragraph("RESUME TYPE", s["small_heading"]),
        Paragraph("Synthetic sample resume for ResumeIQ testing.", s["muted"]),
    ]


def main_content(data, s):
    skills = data["skills"]
    return [
        Paragraph(data["name"], s["name"]),
        Paragraph(data["role"], s["role"]),
        Paragraph("PROFESSIONAL SUMMARY", s["heading"]),
        Paragraph(
            f"{data['role']} with {data['years']} years of experience who has {data['focus']}. "
            f"Comfortable with {', '.join(skills[:5])}, structured problem solving, and delivery-focused teamwork.",
            s["body"],
        ),
        Paragraph("EXPERIENCE", s["heading"]),
        Paragraph(f"{data['role']} | {data['company']} | 2022 - Present", s["body"]),
        bullet_list(
            [
                f"Used {skills[0]}, {skills[1]}, and {skills[2]} to deliver reliable project outcomes for internal teams.",
                f"Improved delivery quality and reduced repeated manual work by {10 + data['years']}% through structured workflows.",
                f"Coordinated reviews with cross-functional teams around {data['project']} goals.",
            ],
            s["body"],
        ),
        Paragraph(f"Associate {data['role']} | {data['previous_company']} | 2020 - 2022", s["body"]),
        bullet_list(
            [
                f"Supported delivery tasks involving {skills[3]}, {skills[4]}, and {skills[5]}.",
                f"Prepared practical notes, issue logs, or validation updates for the {data['project']} initiative.",
            ],
            s["body"],
        ),
        Paragraph("PROJECTS", s["heading"]),
        Paragraph(f"{data['project'].title()} Project", s["body"]),
        bullet_list(
            [
                f"Created a practical project using {', '.join(skills[:4])} to solve a realistic business problem.",
                "Documented project goals, implementation choices, validation steps, and measurable outcomes.",
            ],
            s["body"],
        ),
        Paragraph("EDUCATION", s["heading"]),
        Paragraph("Bachelor's Degree in Relevant Discipline | City Institute of Technology | 2020", s["body"]),
        Paragraph("ADDITIONAL DETAILS", s["heading"]),
        Paragraph("Languages: English, Hindi. Availability: Immediate to 30 days. Preferred mode: Hybrid or remote.", s["body"]),
    ]


def make_left_sidebar(doc, data, s, accent, light, dark):
    table = Table(
        [[sidebar_content(data, s, accent), main_content(data, s)]],
        colWidths=[2.1 * inch, 4.9 * inch],
    )
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), hex_color(light)),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LINEBEFORE", (1, 0), (1, 0), 1, hex_color(accent)),
    ]))
    doc.append(table)


def make_right_sidebar(doc, data, s, accent, light, dark):
    table = Table(
        [[main_content(data, s), sidebar_content(data, s, accent)]],
        colWidths=[4.9 * inch, 2.1 * inch],
    )
    table.setStyle(TableStyle([
        ("BACKGROUND", (1, 0), (1, 0), hex_color(light)),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LINEAFTER", (0, 0), (0, 0), 1, hex_color(accent)),
    ]))
    doc.append(table)


def make_top_band(doc, data, s, accent, light, dark):
    header = Table(
        [[Paragraph(data["name"], s["name_white"])], [Paragraph(f"{data['role']} | {data['email']} | {data['phone']}", s["role_white"])]],
        colWidths=[7.0 * inch],
    )
    header.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), hex_color(accent)),
        ("TOPPADDING", (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    doc.extend([header, Spacer(1, 8)])
    table = Table(
        [[main_content(data, s), sidebar_content(data, s, accent)]],
        colWidths=[4.65 * inch, 2.35 * inch],
    )
    table.setStyle(TableStyle([
        ("BACKGROUND", (1, 0), (1, 0), hex_color(light)),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
    ]))
    doc.append(table)


def make_split_header(doc, data, s, accent, light, dark):
    header = Table(
        [[Paragraph(data["name"], s["name_white"]), Paragraph(f"{data['email']}<br/>{data['phone']}<br/>{data['city']}, India", s["small"])]],
        colWidths=[4.35 * inch, 2.65 * inch],
    )
    header.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), hex_color(accent)),
        ("BACKGROUND", (1, 0), (1, 0), hex_color(light)),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
    ]))
    doc.extend([header, Spacer(1, 8), Paragraph(data["role"], s["role"])])
    table = Table(
        [[sidebar_content(data, s, accent), main_content(data, s)]],
        colWidths=[2.25 * inch, 4.75 * inch],
    )
    table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("LINEAFTER", (0, 0), (0, 0), 1, hex_color(light)),
    ]))
    doc.append(table)


def make_minimal(doc, data, s, accent, light, dark):
    centered_name = ParagraphStyle("CenteredName", parent=s["name"], alignment=TA_CENTER, textColor=colors.HexColor("#111827"))
    centered_role = ParagraphStyle("CenteredRole", parent=s["role"], alignment=TA_CENTER)
    doc.extend([
        Paragraph(data["name"], centered_name),
        Paragraph(f"{data['role']} | {data['email']} | {data['phone']}", centered_role),
        HRFlowable(width="100%", thickness=2, color=hex_color(accent), spaceBefore=4, spaceAfter=10),
    ])
    table = Table(
        [[main_content(data, s), sidebar_content(data, s, accent)]],
        colWidths=[4.9 * inch, 2.1 * inch],
    )
    table.setStyle(TableStyle([
        ("BACKGROUND", (1, 0), (1, 0), hex_color(light)),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
    ]))
    doc.append(table)


LAYOUT_BUILDERS = {
    "left_sidebar": make_left_sidebar,
    "right_sidebar": make_right_sidebar,
    "top_band": make_top_band,
    "split_header": make_split_header,
    "minimal": make_minimal,
}


def create_resume(index):
    data = candidate(index)
    accent, light, dark = PALETTES[index % len(PALETTES)]
    layout = LAYOUTS[index % len(LAYOUTS)]
    s = styles(accent)
    story = []

    LAYOUT_BUILDERS[layout](story, data, s, accent, light, dark)

    file_name = f"{index + 1:02d}_{data['name'].lower().replace(' ', '_')}_{data['role'].lower().replace(' ', '_').replace('/', '_')}.pdf"
    path = OUTPUT_DIR / file_name
    doc = SimpleDocTemplate(
        str(path),
        pagesize=letter,
        rightMargin=0.55 * inch,
        leftMargin=0.55 * inch,
        topMargin=0.55 * inch,
        bottomMargin=0.55 * inch,
        title=f"{data['name']} Resume",
        author="ResumeIQ Synthetic Data Generator",
    )
    doc.build(story)
    return path


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for existing in OUTPUT_DIR.glob("*.pdf"):
        existing.unlink()

    created = [create_resume(index) for index in range(100)]

    if ZIP_PATH.exists():
        ZIP_PATH.unlink()
    with ZipFile(ZIP_PATH, "w", ZIP_DEFLATED) as zip_file:
        for path in created:
            zip_file.write(path, arcname=path.name)

    print(f"Created {len(created)} synthetic visual PDF resumes")
    print(ZIP_PATH)


if __name__ == "__main__":
    main()
