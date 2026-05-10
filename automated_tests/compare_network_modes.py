"""Compare full ResumeIQ pipeline results in offline and online modes."""

from run_full_pipeline_check import run_check


COMPARABLE_FIELDS = [
    "resumes_uploaded",
    "candidates_created",
    "average_match",
    "average_semantic",
    "average_skill_match",
    "top_skill",
    "most_missing_skill",
    "top_candidate",
    "match_distribution_total",
    "semantic_distribution_total",
    "domain_distribution_total",
]


def main():
    offline = run_check("offline")
    online = run_check("online")

    mismatches = []
    for field in COMPARABLE_FIELDS:
        if offline[field] != online[field]:
            mismatches.append((field, offline[field], online[field]))

    if mismatches:
        for field, offline_value, online_value in mismatches:
            print(f"{field}: offline={offline_value!r}, online={online_value!r}")
        raise SystemExit("Offline and online pipeline summaries differ.")

    print("Offline and online pipeline summaries match.")
    print(f"Resumes checked: {offline['resumes_uploaded']}")
    print(f"Average match: {offline['average_match']}%")
    print(f"Average semantic: {offline['average_semantic']}%")


if __name__ == "__main__":
    main()
