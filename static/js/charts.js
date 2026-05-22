/**
 * Chart.js initialization for REx.sane dashboard.
 * Reads data passed from the Django template and renders charts.
 */

function initDashboardCharts(spentData, budgetData, barLabels, barData) {
    // Detect dark mode
    const isDark = document.documentElement.classList.contains('dark');
    const textColor = isDark ? '#94a3b8' : '#64748b';
    const gridColor = isDark ? 'rgba(51, 65, 85, 0.5)' : 'rgba(226, 232, 240, 0.8)';

    // ── Doughnut Chart ──────────────────────────────────────────
    const doughnutCtx = document.getElementById('doughnut-chart');
    if (doughnutCtx) {
        const totalSpent = spentData[0] + spentData[1] + spentData[2];
        const totalBudget = budgetData[0] + budgetData[1] + budgetData[2];
        const remaining = Math.max(0, totalBudget - totalSpent);

        new Chart(doughnutCtx, {
            type: 'doughnut',
            data: {
                labels: ['Needs', 'Wants', 'Savings', 'Remaining'],
                datasets: [{
                    data: [...spentData, remaining],
                    backgroundColor: [
                        '#ef4444',  // Needs — red
                        '#f59e0b',  // Wants — amber
                        '#10b981',  // Savings — emerald
                        isDark ? '#1e293b' : '#e2e8f0',  // Remaining — gray
                    ],
                    borderColor: isDark ? '#0f172a' : '#ffffff',
                    borderWidth: 3,
                    hoverOffset: 6,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                cutout: '65%',
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: textColor,
                            padding: 16,
                            usePointStyle: true,
                            pointStyleWidth: 8,
                            font: { size: 11, family: 'Inter', weight: '500' },
                        }
                    },
                    tooltip: {
                        backgroundColor: isDark ? '#1e293b' : '#fff',
                        titleColor: isDark ? '#e2e8f0' : '#334155',
                        bodyColor: isDark ? '#94a3b8' : '#64748b',
                        borderColor: isDark ? '#334155' : '#e2e8f0',
                        borderWidth: 1,
                        cornerRadius: 10,
                        padding: 12,
                        bodyFont: { family: 'Inter' },
                        callbacks: {
                            label: function(ctx) {
                                return ` ₹${ctx.parsed.toLocaleString('en-IN')}`;
                            }
                        }
                    }
                }
            }
        });
    }

    // ── Bar Chart ────────────────────────────────────────────────
    const barCtx = document.getElementById('bar-chart');
    if (barCtx) {
        new Chart(barCtx, {
            type: 'bar',
            data: {
                labels: barLabels,
                datasets: [{
                    label: 'Daily Spending',
                    data: barData,
                    backgroundColor: function(ctx) {
                        const chart = ctx.chart;
                        const { ctx: c, chartArea } = chart;
                        if (!chartArea) return '#5c7cfa';
                        const gradient = c.createLinearGradient(0, chartArea.top, 0, chartArea.bottom);
                        gradient.addColorStop(0, 'rgba(92, 124, 250, 0.8)');
                        gradient.addColorStop(1, 'rgba(92, 124, 250, 0.2)');
                        return gradient;
                    },
                    borderRadius: 6,
                    borderSkipped: false,
                    maxBarThickness: 28,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: isDark ? '#1e293b' : '#fff',
                        titleColor: isDark ? '#e2e8f0' : '#334155',
                        bodyColor: isDark ? '#94a3b8' : '#64748b',
                        borderColor: isDark ? '#334155' : '#e2e8f0',
                        borderWidth: 1,
                        cornerRadius: 10,
                        padding: 12,
                        bodyFont: { family: 'Inter' },
                        callbacks: {
                            label: function(ctx) {
                                return ` ₹${ctx.parsed.y.toLocaleString('en-IN')}`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: { display: false },
                        ticks: {
                            color: textColor,
                            font: { size: 10, family: 'Inter' },
                            maxTicksLimit: 10,
                        },
                        border: { display: false },
                    },
                    y: {
                        grid: { color: gridColor },
                        ticks: {
                            color: textColor,
                            font: { size: 10, family: 'Inter' },
                            callback: function(value) {
                                if (value >= 100000) return '₹' + (value / 100000).toFixed(1) + 'L';
                                if (value >= 1000) return '₹' + (value / 1000).toFixed(0) + 'K';
                                return '₹' + value;
                            }
                        },
                        border: { display: false },
                    }
                }
            }
        });
    }
}
