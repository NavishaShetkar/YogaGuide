// Wait for page to load
document.addEventListener("DOMContentLoaded", () => {
  // === Accuracy Improvement Chart ===
  const ctx1 = document.getElementById('accuracyChart').getContext('2d');

  new Chart(ctx1, {
    type: 'line',
    data: {
      labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
      datasets: [{
        label: 'Pose Accuracy (%)',
        data: [70, 75, 82, 88, 93, 97],
        borderColor: '#8E44AD',
        backgroundColor: 'rgba(142, 68, 173, 0.15)',
        fill: true,
        borderWidth: 3,
        pointBackgroundColor: '#6A1B9A',
        tension: 0.4, // smooth curve
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: true, labels: { color: '#5E35B1' } },
      },
      scales: {
        x: {
          ticks: { color: '#6A1B9A' },
          grid: { color: 'rgba(142,68,173,0.05)' }
        },
        y: {
          beginAtZero: true,
          max: 100,
          ticks: { color: '#6A1B9A' },
          grid: { color: 'rgba(142,68,173,0.05)' }
        }
      }
    }
  });

  // === Weekly Session Count Chart ===
  const ctx2 = document.getElementById('sessionChart').getContext('2d');

  new Chart(ctx2, {
    type: 'bar',
    data: {
      labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
      datasets: [{
        label: 'Sessions per Day',
        data: [1, 2, 1, 3, 2, 4, 3],
        backgroundColor: [
          '#BB8FCE', '#A569BD', '#9B59B6', '#8E44AD', '#7D3C98', '#6C3483', '#5B2C6F'
        ],
        borderRadius: 8,
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: false }
      },
      scales: {
        x: {
          ticks: { color: '#6A1B9A' },
          grid: { display: false }
        },
        y: {
          beginAtZero: true,
          ticks: { color: '#6A1B9A' },
          grid: { color: 'rgba(142,68,173,0.05)' }
        }
      }
    }
  });
});