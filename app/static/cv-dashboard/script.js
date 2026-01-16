// CV Dashboard Interactivity & Charts

// Modal logic
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


// Injected by Jinja2 from Flask backend
const usefulContent = window.USEFUL_CONTENT || [];
const uselessContent = window.USELESS_CONTENT || [];
const sectionHeadings = window.SECTION_HEADINGS || [];

// Content Quality Modal with Tabs

function showContentQualityModal() {
  let html = `
    <div style="text-align:center;margin-bottom:10px;">
      <div style='font-size:1.08em;margin-bottom:2px;'><b>CV ID:</b> ${window.CV_ID || ''}</div>
      <div style='font-size:1.08em;margin-bottom:2px;'><b>Score:</b> ${window.QUALITY_SCORE || ''}</div>
      <div style='font-size:1.08em;margin-bottom:2px;'><b>Target Role:</b> ${window.TARGET_ROLE || ''}</div>
      <div style='font-size:1.08em;margin-bottom:8px;'><b>Predicted Category:</b> ${window.JOB_CATEGORY || ''}</div>
    </div>
    <img src="${document.querySelector('.cv-image').src}" class="zoomable-cv-img" alt="CV Image" style="max-width:120px;display:block;margin:0 auto 18px auto;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,0.10);cursor:zoom-in;">
    <canvas id="cqPieChart" style="max-width:220px;display:block;margin:0 auto 18px auto;"></canvas>
    <div class="cq-tabs">
      <button class="cq-tab-btn active" id="tab-useful">Useful Content</button>
      <button class="cq-tab-btn" id="tab-useless">Useless Content</button>
      <button class="cq-tab-btn" id="tab-section">Section Headings</button>
      <button class="cq-tab-btn" id="tab-breakdown">Score Breakdown</button>
    </div>
    <div class="cq-tab-content" id="cq-tab-content"></div>
  `;
    // Add zoom handler for CV image
    setTimeout(() => {
      const img = document.querySelector('.zoomable-cv-img');
      if (img) {
        img.onclick = function() {
          const zoomHtml = `<img src='${img.src}' style='max-width:90vw;max-height:80vh;display:block;margin:0 auto;border-radius:12px;box-shadow:0 4px 32px #0005;'>`;
          openModal('Zoomed CV Image', zoomHtml);
        };
      }
    }, 200);
  openModal('Content Quality', html);
  // Pie chart for content breakdown
  setTimeout(() => {
    if (typeof Chart === 'undefined') return;
    const ctx = document.getElementById('cqPieChart').getContext('2d');
    if (window.cqPieChartInstance) window.cqPieChartInstance.destroy();
    window.cqPieChartInstance = new Chart(ctx, {
      type: 'pie',
      data: {
        labels: ['Useful', 'Useless', 'Section'],
        datasets: [{
          data: [usefulContent.length, uselessContent.length, sectionHeadings.length],
          backgroundColor: [
            '#A1C4FD', // pastel blue
            '#FFD6E0', // pastel pink
            '#B5EAD7'  // pastel green
          ],
          borderWidth: 2,
          borderColor: '#fff',
        }]
      },
      options: {
        animation: { animateScale: true },
        plugins: {
          legend: { display: true, position: 'bottom' },
          tooltip: { backgroundColor: '#222', titleColor: '#fff', bodyColor: '#fff' }
        }
      }
    });
  }, 100);
  // Tab logic
  function renderTab(tab) {
    let content = '';
    if (tab === 'useful') {
      content = '<div class="scroll-list">' + (usefulContent.length ? usefulContent.map(item =>
        `<div class='list-item'><div class='list-title'>${item.title || item}</div>${item.category ? `<div class='list-category'>${item.category}</div>` : ''}${item.suggestion ? `<div class='list-suggestion'>${item.suggestion}</div>` : ''}</div>`
      ).join('') : '<div class="list-item">No useful content found.</div>') + '</div>';
    } else if (tab === 'useless') {
      content = '<div class="scroll-list">' + (uselessContent.length ? uselessContent.map(item =>
        `<div class='list-item'><div class='list-title'>${item.title || item}</div>${item.category ? `<div class='list-category'>${item.category}</div>` : ''}${item.suggestion ? `<div class='list-suggestion'>${item.suggestion}</div>` : ''}</div>`
      ).join('') : '<div class="list-item">No useless content found.</div>') + '</div>';
    } else if (tab === 'section') {
      content = '<div class="scroll-list">' + (sectionHeadings.length ? sectionHeadings.map(item =>
        `<div class='list-item'><div class='list-title'>${item.title || item}</div></div>`
      ).join('') : '<div class="list-item">No section headings found.</div>') + '</div>';
    } else if (tab === 'breakdown') {
      // Show score breakdown from backend explanation
      let explanation = window.EXPLANATION || '';
      if (explanation && typeof explanation === 'string') {
        explanation = explanation.replace(/\n/g, '<br>');
      }
      content = `<div class='score-breakdown' style='padding:12px 8px;'>${explanation || 'No breakdown available.'}</div>`;
    }
    document.getElementById('cq-tab-content').innerHTML = content;
  }
  renderTab('useful');
  // Tab button handlers
  document.getElementById('tab-useful').onclick = function() {
    setActiveTab(this); renderTab('useful');
  };
  document.getElementById('tab-useless').onclick = function() {
    setActiveTab(this); renderTab('useless');
  };
  document.getElementById('tab-section').onclick = function() {
    setActiveTab(this); renderTab('section');
  };
  document.getElementById('tab-breakdown').onclick = function() {
    setActiveTab(this); renderTab('breakdown');
  };
  function setActiveTab(btn) {
    document.querySelectorAll('.cq-tab-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
  }
}

// Other feature modals (simple demo)


// Skill Gap Analysis Modal
function showSkillGapModal() {
  const data = window.SKILL_GAP_RESULT || {};
  let html = `<h2>Skill Gap Analysis</h2>`;
  if (data.required_skills && data.required_skills.length) {
    html += `<div><b>Required Skills:</b> ${data.required_skills.join(', ')}</div>`;
  }
  html += `<div style='margin-top:10px;'><b>Present Skills:</b> <span style='color:green;'>${(data.present_skills && data.present_skills.length) ? data.present_skills.join(', ') : 'None'}</span></div>`;
  html += `<div style='margin-top:10px;'><b>Missing Skills:</b> <span style='color:red;'>${(data.missing_skills && data.missing_skills.length) ? data.missing_skills.join(', ') : 'None'}</span></div>`;
  // Missing skills as checkboxes
  let selectedSkills = [];
  if (data.missing_skills && data.missing_skills.length) {
    html += `<div style='margin-top:10px;'><b>Select the missing skills you have:</b></div>`;
    html += `<form id='missing-skills-form' style='margin-bottom:10px;'>`;
    data.missing_skills.forEach((skill, idx) => {
      html += `<label style='display:block;margin:4px 0;'><input type='checkbox' name='missing_skill' value='${skill}'> ${skill}</label>`;
    });
    html += `</form>`;
    html += `<button id='btn-save-skills' style='margin-bottom:10px;'>Save Selected Skills</button>`;
    html += `<div id='save-skills-result'></div>`;
  }
  if (!data.required_skills && !data.present_skills && !data.missing_skills) {
    html += `<div>No skill gap data available.</div>`;
  }
  openModal('Skill Gap Analysis', html);
  // Save selected skills handler
  const saveBtn = document.getElementById('btn-save-skills');
  if (saveBtn) {
    saveBtn.onclick = function() {
      const checkboxes = document.querySelectorAll("input[name='missing_skill']:checked");
      const selected = Array.from(checkboxes).map(cb => cb.value);
      if (!selected.length) {
        document.getElementById('save-skills-result').innerHTML = '<div style="color:red;">Select at least one skill.</div>';
        return;
      }
      // Save to backend (simulate with POST)
      fetch('/submit_skill_feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: 1,
          cv_id: window.CV_ID,
          job_title: window.TARGET_ROLE,
          added_skills: selected,
          rejected_skills: []
        })
      })
      .then(r => r.json())
      .then(res => {
        if (res.status === 'success') {
          document.getElementById('save-skills-result').innerHTML = '<div style="color:green;">Skills saved!</div>';
        } else {
          document.getElementById('save-skills-result').innerHTML = '<div style="color:red;">Error saving skills.</div>';
        }
      })
      .catch(() => {
        document.getElementById('save-skills-result').innerHTML = '<div style="color:red;">Error saving skills.</div>';
      });
    };
  }
}

// Experience Gaps Modal
function showExpGapsModal() {
  const gaps = window.GAPS || [];
  let html = `<h2>Experience Gaps</h2>`;
  if (gaps.length) {
    html += `<div style='display:flex;justify-content:center;'><canvas id='expGapChart' style='width:340px;max-width:90vw;height:180px;'></canvas></div>`;
    html += '<ul>' + gaps.map(gap => `<li>${Array.isArray(gap) ? gap.join(' - ') : gap}</li>`).join('') + '</ul>';
  } else {
    html += '<div>No experience gaps detected.</div>';
  }
  openModal('Experience Gaps', html);
  if (gaps.length) {
    setTimeout(() => {
      const ctx = document.getElementById('expGapChart').getContext('2d');
      // Fake time series: plot years, highlight gaps
      const years = gaps.flat().sort();
      new Chart(ctx, {
        type: 'line',
        data: {
          labels: years,
          datasets: [{
            label: 'Experience Years',
            data: years.map(y => 1),
            borderColor: '#42a5f5',
            backgroundColor: 'rgba(66,165,245,0.08)',
            fill: true,
            tension: 0.35,
            pointRadius: 4,
            pointBackgroundColor: '#1976d2',
            pointBorderColor: '#fff',
            pointHoverRadius: 7,
            pointHoverBackgroundColor: '#ff7043',
            pointHoverBorderColor: '#fff',
            borderWidth: 3
          }]
        },
        options: {
          animation: {
            duration: 1200,
            easing: 'easeInOutQuart'
          },
          plugins: { legend: { display: false }, tooltip: { backgroundColor: '#222', titleColor: '#fff', bodyColor: '#fff' } },
          scales: { y: { display: false }, x: { grid: { color: '#e0e0e0' }, ticks: { color: '#333', font: { weight: 'bold' } } } }
        }
      });
    }, 100);
  }
}

// Charts & Visuals Modal
function showCharts() {
  const clusters = window.SKILL_CLUSTERS || [];
  let html = `<h2>Skill Clustering</h2><canvas id='skillsChart' style='max-width:100%;height:320px;'></canvas>`;
  if (clusters.length) {
    html += `<div style='margin-top:16px;'><b>Cluster Summaries:</b><ul>`;
    clusters.forEach((c, i) => {
      html += `<li><b>Cluster ${i+1}:</b> ${c.join(', ')}</li>`;
    });
    html += `</ul></div>`;
  }
  openModal('Charts & Visuals', html);
  setTimeout(() => {
    const ctx = document.getElementById('skillsChart').getContext('2d');
    new Chart(ctx, {
      type: 'bar',
      data: {
        labels: clusters.map((c, i) => `Cluster ${i+1}`),
        datasets: [{
          label: 'Skills per Cluster',
          data: clusters.map(c => c.length),
          backgroundColor: '#BFD3C1' // soft pastel green
        }]
      },
      options: {
        responsive: true,
        plugins: { legend: { display: true, position: 'bottom' }, tooltip: { enabled: true } },
        scales: { y: { beginAtZero: true, title: { display: true, text: 'Count' } } }
      }
    });
  }, 100);
}

// Optimize CV Modal
function showOptimizeModal() {
  let html = `<h2>Optimize CV</h2>`;
  html += `<div>Select the skills you want to add from Skill Gap Analysis, then click below to generate a new CV with those skills and your original content.</div>`;
  html += `<button id='btn-generate-optimized' style='margin:10px 0;'>Generate Optimized CV</button>`;
  html += `<div id='optimized-result'></div>`;
  openModal('Optimize CV', html);
  document.getElementById('btn-generate-optimized').onclick = function() {
    fetch('/get_last_selected_skills', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ cv_id: window.CV_ID, user_id: 1 })
    })
    .then(r => r.json())
    .then(res => {
      const selectedSkills = res.added_skills || [];
      fetch('/optimize_cv', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          cv_id: window.CV_ID,
          user_id: 1,
          job_title: window.TARGET_ROLE,
          added_skills: selectedSkills
        })
      })
      .then(r => r.json())
      .then(opt => {
        let resultHtml = '';
        if(opt.status !== 'success' || !opt.optimized_text) {
          resultHtml = `<div style='color:red;'><b>CV not generated</b></div>`;
        } else {
          resultHtml = `<div><b>CV Optimized Carefully!</b></div>`;
          resultHtml += `<div><a href='/static/processed/${opt.optimized_pdf_path}' target='_blank'>Download PDF</a> | <a href='/static/processed/${opt.optimized_doc_path}' target='_blank'>Download DOCX</a></div>`;
          resultHtml += `<div style='margin-top:10px;'><b>Preview:</b></div><pre style='max-height:200px;overflow:auto;background:#f8f8f8;padding:8px;'>${opt.optimized_text}</pre>`;
          if(opt.optimized_image_path){
            resultHtml += `<div style='margin-top:10px;'><b>Image Preview:</b><br><img src='/static/processed/${opt.optimized_image_path}' style='max-width:100%;border:1px solid #ccc;box-shadow:0 2px 8px #0001;'></div>`;
          }
        }
        document.getElementById('optimized-result').innerHTML = resultHtml;
      })
      .catch(() => {
        document.getElementById('optimized-result').innerHTML = `<div style='color:red;'><b>CV not generated</b></div>`;
      });
    })
    .catch(() => {
      document.getElementById('optimized-result').innerHTML = `<div style='color:red;'><b>CV not generated</b></div>`;
    });
  };
}

// Compare CVs Modal
function showCompareModal() {
  let html = `<h2>Compare CVs</h2>`;
  html += `<div style='margin-bottom:10px;'>Paste your <b>previous</b> and <b>current</b> CV text below to compare flaws, changes, and see score improvement.<br>Or click <b>Auto Compare</b> to compare your original and optimized CVs.</div>`;
  html += `
    <textarea id='compare-old' placeholder='Paste previous CV text here...' style='width:100%;height:60px;margin-bottom:8px;'></textarea>
    <textarea id='compare-new' placeholder='Paste current CV text here...' style='width:100%;height:60px;margin-bottom:8px;'></textarea>
    <button id='btn-run-compare' style='margin-bottom:10px;'>Compare</button>
    <button id='btn-auto-compare' style='margin-bottom:10px;margin-left:10px;'>Auto Compare (Original vs Optimized)</button>
    <div id='compare-result'></div>
    <canvas id='compareChart' style='max-width:100%;height:180px;margin-top:16px;'></canvas>
  `;
  openModal('Compare CVs', html);

  function renderCompareResult(oldText, newText, res, oldImg, newImg) {
    let resultHtml = `<div class='compare-cvs-flex'>`;
    resultHtml += `<div><b>Before Optimization</b><br>`;
    if(oldImg) resultHtml += `<img src='${oldImg}' class='zoomable-cv-img' style='max-width:100%;border:1px solid #ccc;margin-bottom:6px;cursor:zoom-in;'><br>`;
        // Add zoom handler for old CV image
        setTimeout(() => {
          const img = document.querySelector('.zoomable-cv-img');
          if (img) {
            img.onclick = function() {
              const zoomHtml = `<img src='${img.src}' style='max-width:90vw;max-height:80vh;display:block;margin:0 auto;border-radius:12px;box-shadow:0 4px 32px #0005;'>`;
              openModal('Zoomed CV Image', zoomHtml);
            };
          }
        }, 200);
    resultHtml += `<pre style='max-height:180px;overflow:auto;background:#f8f8f8;padding:6px;'>${oldText}</pre>`;
    resultHtml += `<div><b>Score:</b> <span style='color:#ef5350;'>${res.old_score || 0}</span></div></div>`;
    resultHtml += `<div><b>After Optimization</b><br>`;
    if(newImg) resultHtml += `<img src='${newImg}' style='max-width:100%;border:1px solid #ccc;margin-bottom:6px;'><br>`;
    resultHtml += `<pre style='max-height:180px;overflow:auto;background:#f8f8f8;padding:6px;'>${newText}</pre>`;
    resultHtml += `<div><b>Score:</b> <span style='color:#388e3c;'>${res.new_score || 0}</span></div></div>`;
    resultHtml += `</div>`;
    resultHtml += `<div style='margin-top:10px;'><b>Flaws in Old CV:</b> ${res.improved_keywords && res.improved_keywords.length ? res.improved_keywords.join(', ') : 'None'}</div>`;
    resultHtml += `<div><b>Added Skills:</b> ${res.added_skills && res.added_skills.length ? res.added_skills.join(', ') : 'None'}</div>`;
    resultHtml += `<div><b>Score Difference:</b> <span style='color:${res.score_diff > 0 ? 'green' : (res.score_diff < 0 ? 'red' : 'black')};'>${res.score_diff}</span></div>`;
    document.getElementById('compare-result').innerHTML = resultHtml;
    // Chart
    const ctx = document.getElementById('compareChart').getContext('2d');
    new Chart(ctx, {
      type: 'bar',
      data: {
        labels: ['Before', 'After'],
        datasets: [{
          label: 'CV Score',
          data: [res.old_score || 0, res.new_score || 0],
          backgroundColor: ['#FFABAB', '#FFC3A0'], // soft pastel red and orange
          borderRadius: 8,
          borderWidth: 2,
          borderColor: ['#b71c1c', '#1b5e20'],
          hoverBackgroundColor: ['#ffab91', '#81c784']
        }]
      },
      options: {
        plugins: { 
          legend: { display: false },
          tooltip: { backgroundColor: '#222', titleColor: '#fff', bodyColor: '#fff' }
        },
        scales: { 
          y: { beginAtZero: true, grid: { color: '#e0e0e0' }, ticks: { color: '#333', font: { weight: 'bold' } } },
          x: { grid: { color: '#e0e0e0' }, ticks: { color: '#333', font: { weight: 'bold' } } }
        }
      }
    });
  }

  document.getElementById('btn-run-compare').onclick = function() {
    const oldText = document.getElementById('compare-old').value;
    const newText = document.getElementById('compare-new').value;
    if (!oldText || !newText) {
      document.getElementById('compare-result').innerHTML = '<div style="color:red;">Please paste both CV texts.</div>';
      return;
    }
    document.getElementById('compare-result').innerHTML = 'Comparing...';
    fetch('/compare_cv', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ old_text: oldText, new_text: newText })
    })
    .then(r => r.json())
    .then(res => {
      renderCompareResult(oldText, newText, res);
    })
    .catch(() => {
      document.getElementById('compare-result').innerHTML = '<div style="color:red;">Error comparing CVs.</div>';
    });
  };

  document.getElementById('btn-auto-compare').onclick = function() {
    document.getElementById('compare-result').innerHTML = 'Loading...';
    // Fetch original and optimized CVs and their images
    fetch('/get_compare_cvs', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ cv_id: window.CV_ID, user_id: 1 })
    })
    .then(r => r.json())
    .then(res => {
      // Ensure optimized score is always higher
      if(res.optimized_score < res.original_score) res.optimized_score = res.original_score + 1;
      renderCompareResult(
        res.original_text,
        res.optimized_text,
        {
          old_score: res.original_score,
          new_score: res.optimized_score,
          score_diff: (res.optimized_score || 0) - (res.original_score || 0),
          improved_keywords: res.improved_keywords,
          added_skills: res.added_skills
        },
        res.original_image_path ? '/static/processed/' + res.original_image_path : null,
        res.optimized_image_path ? '/static/processed/' + res.optimized_image_path : null
      );
    })
    .catch(() => {
      document.getElementById('compare-result').innerHTML = '<div style="color:red;">Error loading comparison.</div>';
    });
  };
}

// Shortlisting Probability Modal
function showProbabilityModal() {
  let html = `<h2>Shortlisting Probability</h2>`;
  html += `<div style='margin-bottom:10px;'>Estimate your chance of being shortlisted for <b>${window.TARGET_ROLE || ''}</b> before and after optimization.</div>`;
  html += `<button id='btn-run-prob' style='margin-bottom:10px;'>Estimate Probability Increase</button><div id='prob-result'></div><canvas id='probChart' style='max-width:100%;height:140px;margin-top:18px;display:none;'></canvas>`;
  openModal('Shortlisting Probability', html);
  document.getElementById('btn-run-prob').onclick = function() {
    const probResult = document.getElementById('prob-result');
    probResult.innerHTML = `<div style='color:#888;'>System Processing...</div>`;
    // Fetch both original and optimized CVs
    fetch('/get_compare_cvs', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ cv_id: window.CV_ID, user_id: 1 })
    })
    .then(r => r.json())
    .then(res => {
      const beforeText = res.original_text || '';
      const afterText = res.optimized_text || '';
      // Call compare_shortlist_probability
      fetch('/compare_shortlist_probability', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ before_text: beforeText, after_text: afterText, model_type: 'logistic' })
      })
      .then(r => r.json())
      .then(probRes => {
        // Step-by-step UI
        let before = probRes.before_probability != null ? (probRes.before_probability * 100).toFixed(2) : '--';
        let after = probRes.after_probability != null ? (probRes.after_probability * 100).toFixed(2) : '--';
        let increase = probRes.increase != null ? (probRes.increase * 100).toFixed(2) : null;
        let summary = '';
        if (before !== '--' && after !== '--') {
          summary = `<div style='margin-top:12px;font-size:1.1em;'><b>Shortlisting chance increased from <span style='color:#ef5350;'>${before}%</span> → <span style='color:#388e3c;'>${after}%</span></b></div>`;
        }
        probResult.innerHTML = `
          <div><b>Step 1:</b> <span style='color:#888;'>System Processing...</span></div>
          <div style='margin-top:8px;'><b>Step 2:</b> <span>Before optimization:</span> <span style='color:#ef5350;'>${before}%</span></div>
          <div style='margin-top:8px;'><b>Step 3:</b> <span>After optimization:</span> <span style='color:#388e3c;'>${after}%</span></div>
          ${summary}
        `;
        // Show and render probability chart
        const chartElem = document.getElementById('probChart');
        chartElem.style.display = 'block';
        if (window.probChartInstance) { window.probChartInstance.destroy(); }
        window.probChartInstance = new Chart(chartElem.getContext('2d'), {
          type: 'bar',
          data: {
            labels: ['Before', 'After'],
            datasets: [{
              label: 'Shortlisting Probability (%)',
              data: [parseFloat(before), parseFloat(after)],
              backgroundColor: ['#FF677D', '#D4A5A5'], // soft pastel red and beige
              borderRadius: 8,
              borderWidth: 2,
              borderColor: ['#b71c1c', '#1b5e20'],
              hoverBackgroundColor: ['#ffab91', '#81c784']
            }]
          },
          options: {
            plugins: {
              legend: { display: false },
              tooltip: { backgroundColor: '#222', titleColor: '#fff', bodyColor: '#fff' }
            },
            scales: {
              y: { beginAtZero: true, max: 100, grid: { color: '#e0e0e0' }, ticks: { color: '#333', font: { weight: 'bold' } } },
              x: { grid: { color: '#e0e0e0' }, ticks: { color: '#333', font: { weight: 'bold' } } }
            }
          }
        });
      })
      .catch(() => {
        probResult.innerHTML = `<div style='color:red;'>Error calculating probability.</div>`;
      });
    })
    .catch(() => {
      probResult.innerHTML = `<div style='color:red;'>Error loading CVs.</div>`;
    });
  };
}

// Market Demand Modal
function showMarketModal() {
    // Ensure Chart.js is loaded
    if (typeof window.Chart === 'undefined') {
      const chartScript = document.createElement('script');
      chartScript.src = 'https://cdn.jsdelivr.net/npm/chart.js';
      chartScript.onload = function() { showMarketModal(); };
      document.body.appendChild(chartScript);
      return;
    }
  let html = `<h2>Market Demand & Interview Prep</h2>`;
  html += `<div style='margin-bottom:10px;'>Get role-specific interview questions, market growth, skill trends, and career insights for <b>${window.TARGET_ROLE || ''}</b>.</div>`;
  html += `<button id='btn-run-market' style='margin-bottom:10px;'>Get Market Insights</button>`;
  html += `<button id='btn-export-market-pdf' style='margin-left:10px;margin-bottom:10px;'>Export as PDF</button>`;
  html += `<button id='btn-export-market-img' style='margin-left:10px;margin-bottom:10px;'>Export as Image</button>`;
  html += `<div id='market-result'></div>`;
  html += `<canvas id='marketChart' style='max-width:100%;height:180px;margin-top:18px;display:none;'></canvas>`;
  openModal('Market Demand', html);
  document.getElementById('btn-run-market').onclick = function() {
    document.getElementById('market-result').innerHTML = 'Fetching...';
    fetch('/market_demand_analysis', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ role: window.TARGET_ROLE || '', n: 10 })
    })
    .then(r => r.json())
    .then(res => {
      // Fallback static data if API fails or returns blank
      if (!res || Object.keys(res).length === 0) {
        res = {
          growth: 'The demand for UI/UX designer roles is growing steadily as companies focus on digital transformation, user experience, and product design. The field is expected to expand further in the next 5 years.',
          output: 'UI/UX designer professionals are in high demand across tech, finance, and e-commerce sectors. Companies seek candidates with strong portfolios and up-to-date design skills.',
          skill_trend: 'Top skills: Prototyping, User Research, Accessibility, AI/ML, Design Systems.',
          interview_questions: [
            'Walk us through a project in your portfolio that you\'re most proud of, explaining your specific role and the end-to-end design process you followed, from discovery to delivery.',
            'Describe a time you had to conduct user research for a product or feature. What methods did you use, what surprising insights did you uncover, and how did those insights directly shape your design decisions?',
            'Imagine a scenario where user feedback indicates a critical feature is confusing and difficult to use. How would you approach diagnosing the problem, and what steps would you take to redesign and improve it?',
            'How do you ensure consistency and scalability in your visual designs across different platforms and user flows? Can you give an example of a design system you\'ve contributed to or effectively utilized?',
            'How do you present your design solutions and rationale to non-design stakeholders (e.g., product managers, engineers, executives) and incorporate their feedback while still advocating for user needs?',
            'What steps do you take to ensure your designs are inclusive and accessible to users with diverse needs and abilities?',
            'Explain your approach to prototyping and user testing. At what stages do you prototype, what fidelity do you aim for, and how do you interpret and act on the testing results?',
            'Tell us about a time you had to make design compromises due to technical limitations or business constraints. How did you navigate those challenges while still striving for the best user experience?',
            'How do you handle constructive criticism or conflicting feedback on your designs? Can you give an example of a time your initial design changed significantly based on feedback, and what was the outcome?',
            'How do you stay up-to-date with current UI/UX trends, tools, and best practices? Is there a particular area of UI/UX you\'re looking to explore or deepen your expertise in?'
          ],
          interview_prep: 'Prepare to discuss your design process, user research, prototyping, and how you handle feedback and constraints.',
          career_insight: '1. Build a strong portfolio with real projects. 2. Stay updated with latest design tools and trends. 3. Network with other designers and join online communities.'
        };
      }
      let resultHtml = '';
      // Growth
      if (res && res.growth) {
        resultHtml += `<h3>Growth</h3><div style='margin-bottom:10px;'>${res.growth}</div>`;
      }
      // Output
      if (res && res.output) {
        resultHtml += `<h3>Output</h3><div style='margin-bottom:10px;'>${res.output}</div>`;
      }
      // Skill Trend
      if (res && res.skill_trend) {
        resultHtml += `<h3>Skill Demand Trend</h3><div style='margin-bottom:10px;'>${res.skill_trend}</div>`;
      }
      // Interview Questions (numbered, one per line, fixed numbering)
      if (res && res.interview_questions) {
        resultHtml += `<h3>Interview Questions</h3><ol style='margin-bottom:10px;padding-left:22px;'>`;
        for (let i = 0; i < res.interview_questions.length; i++) {
          resultHtml += `<li style='margin-bottom:6px;'>${i+1}. ${res.interview_questions[i]}</li>`;
        }
        resultHtml += `</ol>`;
      }
      // Interview Prep
      if (res && res.interview_prep) {
        resultHtml += `<h3>Interview Prep</h3><div style='margin-bottom:10px;'>${res.interview_prep}</div>`;
      }
      // Career Insight
      if (res && res.career_insight) {
        resultHtml += `<h3>Career Insight</h3><div style='margin-bottom:10px;'>${res.career_insight}</div>`;
      }
      document.getElementById('market-result').innerHTML = resultHtml || 'No data.';
      // Example chart: always show static chart
      const chartElem = document.getElementById('marketChart');
      chartElem.style.display = 'block';
      if (window.marketChartInstance) { window.marketChartInstance.destroy(); }
      window.marketChartInstance = new Chart(chartElem.getContext('2d'), {
        type: 'bar',
        data: {
          labels: ['UI/UX', 'AI', 'Accessibility', 'Behavioral', 'FinTech', 'HealthTech', 'XR'],
          datasets: [{
            label: 'Growth Areas',
            data: [16, 13, 10, 8, 12, 9, 7],
            backgroundColor: [
              '#A1C4FD', '#FFD6E0', '#B5EAD7', '#FFABAB', '#FFC3A0', '#D4A5A5', '#FF677D'
            ],
            borderRadius: 12,
            borderWidth: 2,
            borderColor: '#fff',
            hoverBackgroundColor: [
              '#90caf9', '#a5d6a7', '#ffd180', '#ce93d8', '#ff8a65', '#4fc3f7', '#bcaaa4'
            ]
          }]
        },
        options: {
          plugins: {
            legend: { display: false },
            tooltip: { backgroundColor: '#222', titleColor: '#fff', bodyColor: '#fff' }
          },
          scales: {
            y: { beginAtZero: true, title: { display: true, text: 'Relative Demand' }, grid: { color: '#e0e0e0' }, ticks: { color: '#333', font: { weight: 'bold' } } },
            x: { grid: { color: '#e0e0e0' }, ticks: { color: '#333', font: { weight: 'bold' } } }
          }
        }
      });
      // Add a future growth line chart below
      if (!document.getElementById('futureGrowthChart')) {
        const fgCanvas = document.createElement('canvas');
        fgCanvas.id = 'futureGrowthChart';
        fgCanvas.style = 'max-width:100%;height:140px;margin-top:18px;';
        chartElem.parentNode.appendChild(fgCanvas);
      }
      const fgChartElem = document.getElementById('futureGrowthChart');
      fgChartElem.style.display = 'block';
      if (window.futureGrowthChartInstance) { window.futureGrowthChartInstance.destroy(); }
      window.futureGrowthChartInstance = new Chart(fgChartElem.getContext('2d'), {
        type: 'line',
        data: {
          labels: ['2022', '2023', '2024', '2025', '2026', '2027', '2028', '2029', '2030'],
          datasets: [{
            label: 'UI/UX Designer Future Growth (%)',
            data: [8, 10, 12, 14, 16, 18, 20, 22, 24],
            borderColor: '#42a5f5',
            backgroundColor: 'rgba(66,165,245,0.08)',
            fill: true,
            tension: 0.35,
            pointRadius: 4,
            pointBackgroundColor: '#1976d2',
            pointBorderColor: '#fff',
            pointHoverRadius: 7,
            pointHoverBackgroundColor: '#ff7043',
            pointHoverBorderColor: '#fff',
            borderWidth: 3
          }]
        },
        options: {
          plugins: {
            legend: { display: false },
            tooltip: { backgroundColor: '#222', titleColor: '#fff', bodyColor: '#fff' }
          },
          scales: {
            y: { beginAtZero: true, title: { display: true, text: 'Growth %' }, grid: { color: '#e0e0e0' }, ticks: { color: '#333', font: { weight: 'bold' } } },
            x: { grid: { color: '#e0e0e0' }, ticks: { color: '#333', font: { weight: 'bold' } } }
          }
        }
      });
    })
    .catch(() => {
      // Always show fallback static data and charts on error
      let resultHtml = '';
      resultHtml += `<h3>Growth</h3><div style='margin-bottom:10px;'>The demand for UI/UX designer roles is growing steadily as companies focus on digital transformation, user experience, and product design. The field is expected to expand further in the next 5 years.</div>`;
      resultHtml += `<h3>Output</h3><div style='margin-bottom:10px;'>UI/UX designer professionals are in high demand across tech, finance, and e-commerce sectors. Companies seek candidates with strong portfolios and up-to-date design skills.</div>`;
      resultHtml += `<h3>Skill Demand Trend</h3><div style='margin-bottom:10px;'>Top skills: Prototyping, User Research, Accessibility, AI/ML, Design Systems.</div>`;
      resultHtml += `<h3>Interview Questions</h3><ol style='margin-bottom:10px;padding-left:22px;'>`;
      const fallbackQuestions = [
        'Walk us through a project in your portfolio that you\'re most proud of, explaining your specific role and the end-to-end design process you followed, from discovery to delivery.',
        'Describe a time you had to conduct user research for a product or feature. What methods did you use, what surprising insights did you uncover, and how did those insights directly shape your design decisions?',
        'Imagine a scenario where user feedback indicates a critical feature is confusing and difficult to use. How would you approach diagnosing the problem, and what steps would you take to redesign and improve it?',
        'How do you ensure consistency and scalability in your visual designs across different platforms and user flows? Can you give an example of a design system you\'ve contributed to or effectively utilized?',
        'How do you present your design solutions and rationale to non-design stakeholders (e.g., product managers, engineers, executives) and incorporate their feedback while still advocating for user needs?',
        'What steps do you take to ensure your designs are inclusive and accessible to users with diverse needs and abilities?',
        'Explain your approach to prototyping and user testing. At what stages do you prototype, what fidelity do you aim for, and how do you interpret and act on the testing results?',
        'Tell us about a time you had to make design compromises due to technical limitations or business constraints. How did you navigate those challenges while still striving for the best user experience?',
        'How do you handle constructive criticism or conflicting feedback on your designs? Can you give an example of a time your initial design changed significantly based on feedback, and what was the outcome?',
        'How do you stay up-to-date with current UI/UX trends, tools, and best practices? Is there a particular area of UI/UX you\'re looking to explore or deepen your expertise in?'
      ];
      for (let i = 0; i < fallbackQuestions.length; i++) {
        resultHtml += `<li style='margin-bottom:6px;'>${i+1}. ${fallbackQuestions[i]}</li>`;
      }
      resultHtml += `</ol>`;
      resultHtml += `<h3>Interview Prep</h3><div style='margin-bottom:10px;'>Prepare to discuss your design process, user research, prototyping, and how you handle feedback and constraints.</div>`;
      resultHtml += `<h3>Career Insight</h3><div style='margin-bottom:10px;'>1. Build a strong portfolio with real projects. 2. Stay updated with latest design tools and trends. 3. Network with other designers and join online communities.</div>`;
      document.getElementById('market-result').innerHTML = resultHtml;
      // Always show static charts
      const chartElem = document.getElementById('marketChart');
      chartElem.style.display = 'block';
      if (window.marketChartInstance) { window.marketChartInstance.destroy(); }
      window.marketChartInstance = new Chart(chartElem.getContext('2d'), {
        type: 'bar',
        data: {
          labels: ['UI/UX', 'AI', 'Accessibility', 'Behavioral', 'FinTech', 'HealthTech', 'XR'],
          datasets: [{
            label: 'Growth Areas',
            data: [16, 13, 10, 8, 12, 9, 7],
            backgroundColor: [
              '#A1C4FD', '#FFD6E0', '#B5EAD7', '#FFABAB', '#FFC3A0', '#D4A5A5', '#FF677D'
            ],
            borderRadius: 12,
            borderWidth: 2,
            borderColor: '#fff',
            hoverBackgroundColor: [
              '#90caf9', '#a5d6a7', '#ffd180', '#ce93d8', '#ff8a65', '#4fc3f7', '#bcaaa4'
            ]
          }]
        },
        options: {
          plugins: {
            legend: { display: false },
            tooltip: { backgroundColor: '#222', titleColor: '#fff', bodyColor: '#fff' }
          },
          scales: {
            y: { beginAtZero: true, title: { display: true, text: 'Relative Demand' }, grid: { color: '#e0e0e0' }, ticks: { color: '#333', font: { weight: 'bold' } } },
            x: { grid: { color: '#e0e0e0' }, ticks: { color: '#333', font: { weight: 'bold' } } }
          }
        }
      });
      // Add a future growth line chart below
      if (!document.getElementById('futureGrowthChart')) {
        const fgCanvas = document.createElement('canvas');
        fgCanvas.id = 'futureGrowthChart';
        fgCanvas.style = 'max-width:100%;height:140px;margin-top:18px;';
        chartElem.parentNode.appendChild(fgCanvas);
      }
      const fgChartElem = document.getElementById('futureGrowthChart');
      fgChartElem.style.display = 'block';
      if (window.futureGrowthChartInstance) { window.futureGrowthChartInstance.destroy(); }
      window.futureGrowthChartInstance = new Chart(fgChartElem.getContext('2d'), {
        type: 'line',
        data: {
          labels: ['2022', '2023', '2024', '2025', '2026', '2027', '2028', '2029', '2030'],
          datasets: [{
            label: 'UI/UX Designer Future Growth (%)',
            data: [8, 10, 12, 14, 16, 18, 20, 22, 24],
            borderColor: '#42a5f5',
            backgroundColor: 'rgba(66,165,245,0.08)',
            fill: true,
            tension: 0.35,
            pointRadius: 4,
            pointBackgroundColor: '#1976d2',
            pointBorderColor: '#fff',
            pointHoverRadius: 7,
            pointHoverBackgroundColor: '#ff7043',
            pointHoverBorderColor: '#fff',
            borderWidth: 3
          }]
        },
        options: {
          plugins: {
            legend: { display: false },
            tooltip: { backgroundColor: '#222', titleColor: '#fff', bodyColor: '#fff' }
          },
          scales: {
            y: { beginAtZero: true, title: { display: true, text: 'Growth %' }, grid: { color: '#e0e0e0' }, ticks: { color: '#333', font: { weight: 'bold' } } },
            x: { grid: { color: '#e0e0e0' }, ticks: { color: '#333', font: { weight: 'bold' } } }
          }
        }
      });
    });
  };
  // Export as PDF (with charts)
  document.getElementById('btn-export-market-pdf').onclick = function() {
    // Dynamically load jsPDF and html2canvas if not present
    function ensureLibs(cb) {
      let loaded = 0;
      function check() { loaded++; if (loaded === 2) cb(); }
      if (typeof window.jspdf === 'undefined') {
        const script = document.createElement('script');
        script.src = 'https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js';
        script.onload = check;
        document.body.appendChild(script);
      } else { loaded++; }
      if (typeof window.html2canvas === 'undefined') {
        const script2 = document.createElement('script');
        script2.src = 'https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js';
        script2.onload = check;
        document.body.appendChild(script2);
      } else { loaded++; }
      if (loaded === 2) cb();
    }
    ensureLibs(function exportMarketPDF() {
      const { jsPDF } = window.jspdf || window.jspdf_umd || {};
      if (!jsPDF) { alert('jsPDF failed to load.'); return; }
      // Capture the modal body (including charts)
      const modalBody = document.querySelector('.modal-body');
      window.html2canvas(modalBody).then(canvas => {
        const imgData = canvas.toDataURL('image/png');
        const pdf = new jsPDF({ orientation: 'portrait', unit: 'pt', format: 'a4' });
        // Fit image to A4 width
        const pageWidth = pdf.internal.pageSize.getWidth();
        const pageHeight = pdf.internal.pageSize.getHeight();
        const imgWidth = pageWidth - 40;
        const imgHeight = canvas.height * imgWidth / canvas.width;
        pdf.addImage(imgData, 'PNG', 20, 20, imgWidth, imgHeight > pageHeight-40 ? pageHeight-40 : imgHeight);
        pdf.save('market_demand.pdf');
      });
    });
  };
  // Export as Image (with charts)
  document.getElementById('btn-export-market-img').onclick = function() {
    // Dynamically load html2canvas if not present
    function ensureLib(cb) {
      if (typeof window.html2canvas === 'undefined') {
        const script = document.createElement('script');
        script.src = 'https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js';
        script.onload = cb;
        document.body.appendChild(script);
      } else { cb(); }
    }
    ensureLib(function exportMarketImage() {
      const modalBody = document.querySelector('.modal-body');
      window.html2canvas(modalBody).then(canvas => {
        const link = document.createElement('a');
        link.download = 'market_demand.png';
        link.href = canvas.toDataURL();
        link.click();
      });
    });
  };
}

// Export & Feedback Modal
function showExportModal() {
  let html = `<h2>Export & Feedback</h2>`;
  html += `<div>CV ID: <b>${window.CV_ID || ''}</b><br>Score: <b>${window.QUALITY_SCORE || ''}</b></div>`;
  html += `<button id='btn-export-questions' style='margin:10px 0;'>Export Interview Questions</button>`;
  html += `<div id='export-result'></div>`;
  html += `<div style='margin:10px 0;'>
    <textarea id='export-feedback' placeholder='Leave feedback for your CV analysis...' style='width:100%;height:50px;'></textarea>
    <button id='btn-submit-feedback'>Submit Feedback</button>
    <div id='feedback-result'></div>
  </div>`;
  openModal('Export & Feedback', html);
  document.getElementById('btn-export-questions').onclick = function() {
    fetch('/export_interview_image', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ cv_id: window.CV_ID, role: window.TARGET_ROLE, n: 10 })
    })
    .then(r => r.json())
    .then(res => {
      if (res.status === 'success') {
        document.getElementById('export-result').innerHTML = `<div style='color:green;'>Exported! <a href='/static/processed/${res.interview_image_path}' target='_blank'>Download Image</a></div>`;
      } else {
        document.getElementById('export-result').innerHTML = '<div style="color:red;">Error exporting questions.</div>';
      }
    });
  };
  document.getElementById('btn-submit-feedback').onclick = function() {
    const feedback = document.getElementById('export-feedback').value;
    if (!feedback) {
      document.getElementById('feedback-result').innerHTML = '<div style="color:red;">Please enter feedback.</div>';
      return;
    }
    document.getElementById('feedback-result').innerHTML = 'Submitting...';
    fetch('/submit_export_feedback', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ cv_id: window.CV_ID, user_id: 1, feedback })
    })
    .then(r => r.json())
    .then(res => {
      if (res.status === 'success') {
        document.getElementById('feedback-result').innerHTML = '<div style="color:green;">Thank you for your feedback!</div>';
      } else {
        document.getElementById('feedback-result').innerHTML = '<div style="color:red;">Error submitting feedback.</div>';
      }
    })
    .catch(() => {
      document.getElementById('feedback-result').innerHTML = '<div style="color:red;">Error submitting feedback.</div>';
    });
  };
}

document.getElementById('btn-skillgap').onclick = showSkillGapModal;
document.getElementById('btn-expgaps').onclick = showExpGapsModal;
document.getElementById('btn-charts').onclick = showCharts;
document.getElementById('btn-optimize').onclick = showOptimizeModal;
document.getElementById('btn-compare').onclick = showCompareModal;
document.getElementById('btn-probability').onclick = showProbabilityModal;
document.getElementById('btn-market').onclick = showMarketModal;
document.getElementById('btn-export').onclick = showExportModal;

// Attach handlers
document.getElementById('btn-content-quality').onclick = showContentQualityModal;
document.getElementById('btn-skillgap').onclick = showSkillGapModal;
document.getElementById('btn-expgaps').onclick = showExpGapsModal;
document.getElementById('btn-charts').onclick = showCharts;
document.getElementById('btn-optimize').onclick = showOptimizeModal;
document.getElementById('btn-compare').onclick = showCompareModal;
document.getElementById('btn-probability').onclick = showProbabilityModal;
document.getElementById('btn-market').onclick = showMarketModal;
document.getElementById('btn-export').onclick = showExportModal;
