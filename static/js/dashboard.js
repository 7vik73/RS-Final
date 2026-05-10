const chartData = window.resumeIQCharts || {};

const palette = {
    teal: "#0f766e",
    slate: "#334155",
    orange: "#c2410c",
    blue: "#2563eb",
    amber: "#d97706",
    red: "#dc2626",
    gray: "#94a3b8"
};

function hasValues(values) {
    return Array.isArray(values) && values.some((value) => Number(value) > 0);
}

function baseOptions(xTitle, yTitle, extra = {}) {
    return {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { display: false },
            tooltip: {
                callbacks: {
                    label: (context) => `${context.dataset.label}: ${context.raw}`
                }
            }
        },
        scales: {
            x: {
                beginAtZero: true,
                ticks: { precision: 0 },
                title: { display: true, text: xTitle }
            },
            y: {
                beginAtZero: true,
                ticks: { precision: 0 },
                title: { display: true, text: yTitle }
            }
        },
        ...extra
    };
}

function makeBarChart(canvasId, labels, values, label, color, xTitle, yTitle) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;

    new Chart(canvas, {
        type: "bar",
        data: {
            labels,
            datasets: [{
                label,
                data: values,
                backgroundColor: hasValues(values) ? color : palette.gray,
                borderRadius: 6,
                borderSkipped: false
            }]
        },
        options: baseOptions(xTitle, yTitle)
    });
}

function makeHorizontalBarChart(canvasId, labels, values, label, color) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;

    new Chart(canvas, {
        type: "bar",
        data: {
            labels,
            datasets: [{
                label,
                data: values,
                backgroundColor: hasValues(values) ? color : palette.gray,
                borderRadius: 6,
                borderSkipped: false
            }]
        },
        options: baseOptions("Skill Frequency Count", "Skill Names", {
            indexAxis: "y",
            scales: {
                x: {
                    beginAtZero: true,
                    ticks: { precision: 0 },
                    title: { display: true, text: "Skill Frequency Count" }
                },
                y: {
                    title: { display: true, text: "Skill Names" }
                }
            }
        })
    });
}

function makeDoughnutChart(canvasId, labels, values, label, colors) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;

    new Chart(canvas, {
        type: "doughnut",
        data: {
            labels,
            datasets: [{
                label,
                data: values,
                backgroundColor: hasValues(values) ? colors : [palette.gray],
                borderColor: "#ffffff",
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: "bottom",
                    labels: { boxWidth: 10, usePointStyle: true }
                },
                tooltip: {
                    callbacks: {
                        label: (context) => `${context.label}: ${context.raw} candidates`
                    }
                }
            },
            cutout: "62%"
        }
    });
}

makeBarChart(
    "matchChart",
    chartData.matchDistribution?.labels || [],
    chartData.matchDistribution?.values || [],
    "Candidates",
    palette.teal,
    "Overall Match Score Range",
    "Number of Candidates"
);

makeBarChart(
    "semanticChart",
    chartData.semanticDistribution?.labels || [],
    chartData.semanticDistribution?.values || [],
    "Candidates",
    palette.orange,
    "Semantic Relevance Range",
    "Number of Candidates"
);

makeHorizontalBarChart(
    "skillsChart",
    chartData.topSkills?.labels || [],
    chartData.topSkills?.values || [],
    "Skill Frequency Count",
    palette.slate
);

makeDoughnutChart(
    "domainChart",
    chartData.domainDistribution?.labels || ["No resumes"],
    chartData.domainDistribution?.values || [0],
    "Candidate Domains",
    [palette.teal, palette.blue, palette.orange, palette.amber, "#7c3aed", "#0891b2", "#be123c", "#475569"]
);

makeDoughnutChart(
    "statusChart",
    chartData.statusDistribution?.labels || ["Pending", "Shortlisted", "Rejected"],
    chartData.statusDistribution?.values || [0, 0, 0],
    "Candidate Status",
    [palette.gray, palette.teal, palette.red]
);
