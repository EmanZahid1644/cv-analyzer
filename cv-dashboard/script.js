// CV Dashboard Interactivity & Charts
const modal = document.getElementById('modal');
const modalContent = document.getElementById('modal-content');
const modalTitle = document.getElementById('modal-title');
const closeModalBtn = document.getElementById('close-modal');

function openModal(title, contentHtml) {
  modalTitle.textContent = title;
  modalContent.querySelector('.modal-body').innerHTML = contentHtml;
  modal.classList.add('open');
}
function closeModal() {
  modal.classList.remove('open');
}
closeModalBtn.onclick = closeModal;
modal.onclick = function(e) {
  if (e.target === modal) closeModal();
};
// Example data for demo
const usefulContent = [
  { title: 'Python Developer & Data Analyst', category: 'Skill', suggestion: 'Highlight project outcomes.' },
  { title: 'Remote Assistant – Email Marketing', category: 'Experience', suggestion: 'Quantify campaign results.' },
  { title: 'Data Science Projects', category: 'Keyword', suggestion: '' }
];
const uselessContent = [
  { title: 'FSc Pre-Medical', category: 'Education', suggestion: 'Remove unless relevant.' }
];
// Button handlers
function showUsefulContent() {
  let html = '<div class="scroll-list">';
  usefulContent.forEach(item => {
    html += `<div class='list-item'><div class='list-title'>${item.title}</div><div class='list-category'>${item.category}</div>${item.suggestion ? `<div class='list-suggestion'>${item.suggestion}</div>` : ''}</div>`;
  });
  html += '</div>';
  openModal('Useful Content', html);
}
function showUselessContent() {
  let html = '<div class="scroll-list">';
  uselessContent.forEach(item => {
    html += `<div class='list-item'><div class='list-title'>${item.title}</div><div class='list-category'>${item.category}</div>${item.suggestion ? `<div class='list-suggestion'>${item.suggestion}</div>` : ''}</div>`;
  });
  html += '</div>';
  openModal('Useless Content', html);
}
// Add similar functions for other features (Skill Gap, Experience Gaps, etc.)
// Chart.js example
function showCharts() {
  let html = `<canvas id='skillsChart' style='max-width:100%;height:320px;'></canvas>`;
  openModal('Charts & Visuals', html);
  setTimeout(() => {
    const ctx = document.getElementById('skillsChart').getContext('2d');
    new Chart(ctx, {
      type: 'bar',
      data: {
        labels: ['Cluster 1', 'Cluster 2', 'Cluster 3'],
        datasets: [{
          label: 'Skills per Cluster',
          data: [8, 5, 7],
          backgroundColor: '#7e57c2'
        }]
      },
      options: {
        responsive: true,
        plugins: { legend: { display: true, position: 'bottom' }, tooltip: { enabled: true } },
        scales: { y: { beginAtZero: true, title: { display: true, text: 'Count' } } },
        onClick: (e, elements) => {
          if (elements.length) {
            alert('Drilldown: ' + elements[0].index);
          }
        }
      }
    });
  }, 100);
}
// Attach handlers
document.getElementById('btn-useful').onclick = showUsefulContent;
document.getElementById('btn-useless').onclick = showUselessContent;
document.getElementById('btn-charts').onclick = showCharts;
// ...add for other buttons
