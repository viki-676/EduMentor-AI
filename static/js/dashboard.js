// EduMentor AI - Student Analytics & Chart.js Visualizations
document.addEventListener('DOMContentLoaded', function () {
    // 1. Score History Trend Chart
    const trendCtx = document.getElementById('scoreTrendChart');
    if (trendCtx && window.scoreTimelineData) {
        const labels = window.scoreTimelineData.labels || [];
        const scores = window.scoreTimelineData.scores || [];

        if (labels.length > 0) {
            new Chart(trendCtx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Score Percentage (%)',
                        data: scores,
                        borderColor: '#2563eb',
                        backgroundColor: 'rgba(37, 99, 235, 0.1)',
                        borderWidth: 3,
                        tension: 0.35,
                        fill: true,
                        pointBackgroundColor: '#0a192f',
                        pointBorderColor: '#ffffff',
                        pointBorderWidth: 2,
                        pointRadius: 5,
                        pointHoverRadius: 7
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100,
                            ticks: {
                                callback: function (val) { return val + '%'; }
                            },
                            grid: { color: '#f1f5f9' }
                        },
                        x: {
                            grid: { display: false }
                        }
                    },
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            callbacks: {
                                label: function (context) {
                                    return `Score: ${context.parsed.y}%`;
                                }
                            }
                        }
                    }
                }
            });
        }
    }

    // 2. Topic Accuracy Chart
    const topicCtx = document.getElementById('topicAccuracyChart');
    if (topicCtx && window.topicPerformanceData) {
        const topics = Object.keys(window.topicPerformanceData);
        if (topics.length > 0) {
            const accuracies = topics.map(t => window.topicPerformanceData[t].accuracy);
            const backgroundColors = accuracies.map(acc => {
                if (acc < 50) return '#ef4444'; // Red for critical weak
                if (acc < 70) return '#f59e0b'; // Amber for developing
                return '#0d9488'; // Teal for mastered
            });

            new Chart(topicCtx, {
                type: 'bar',
                data: {
                    labels: topics,
                    datasets: [{
                        label: 'Accuracy (%)',
                        data: accuracies,
                        backgroundColor: backgroundColors,
                        borderRadius: 6,
                        maxBarThickness: 28
                    }]
                },
                options: {
                    indexAxis: 'y',
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: {
                            beginAtZero: true,
                            max: 100,
                            ticks: {
                                callback: function (val) { return val + '%'; }
                            },
                            grid: { color: '#f1f5f9' }
                        },
                        y: {
                            grid: { display: false }
                        }
                    },
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            callbacks: {
                                label: function (context) {
                                    return `Accuracy: ${context.parsed.x}%`;
                                }
                            }
                        }
                    }
                }
            });
        }
    }
});
