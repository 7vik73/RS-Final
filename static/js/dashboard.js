function makeChart(canvasId, type, labels, values, label, color) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;

    new Chart(canvas, {
        type,
        data: {
            labels,
            datasets: [{
                label,
                data: values,
                backgroundColor: color,
                borderColor: color,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false }
            },
            scales: type === "doughnut" ? {} : {
                y: { beginAtZero: true }
            }
        }
    });
}

const chartData = window.resumeIQCharts || {};

makeChart(
    "matchChart",
    "bar",
    chartData.matchDistribution?.labels || [],
    chartData.matchDistribution?.values || [],
    "Candidates",
    "#0f766e"
);

makeChart(
    "skillsChart",
    "bar",
    chartData.topSkills?.labels || [],
    chartData.topSkills?.values || [],
    "Skill Count",
    "#334155"
);

makeChart(
    "semanticChart",
    "line",
    chartData.semanticScores?.labels || [],
    chartData.semanticScores?.values || [],
    "Semantic %",
    "#c2410c"
);
