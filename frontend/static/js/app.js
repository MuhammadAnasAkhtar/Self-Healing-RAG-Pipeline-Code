document.addEventListener('DOMContentLoaded', () => {
    // ===== INTRO OVERLAY =====
    const introOverlay = document.getElementById('intro-overlay');
    const mainApp = document.getElementById('main-app');
    let introSkipped = false;

    function skipIntro() {
        if (introSkipped) return;
        introSkipped = true;
        introOverlay.style.animation = 'none';
        introOverlay.style.opacity = '0';
        setTimeout(() => {
            introOverlay.style.display = 'none';
            mainApp.style.display = 'block';
        }, 400);
    }

    // Skip on click anywhere
    introOverlay.addEventListener('click', skipIntro);
    // Auto-skip after 5 seconds
    setTimeout(() => {
        if (!introSkipped) {
            introOverlay.style.animation = 'fadeOutOverlay 0.5s ease forwards';
            setTimeout(() => {
                introOverlay.style.display = 'none';
                mainApp.style.display = 'block';
            }, 500);
        }
    }, 5000);

    // Generate floating particles
    function createParticles() {
        const container = document.getElementById('particles');
        for (let i = 0; i < 30; i++) {
            const particle = document.createElement('div');
            particle.className = 'particle';
            const size = Math.random() * 6 + 2;
            particle.style.width = size + 'px';
            particle.style.height = size + 'px';
            particle.style.left = Math.random() * 100 + '%';
            particle.style.animationDuration = (Math.random() * 4 + 4) + 's';
            particle.style.animationDelay = Math.random() * 5 + 's';
            particle.style.background = ['#ff6b6b', '#feca57', '#48dbfb', '#ff9ff3'][Math.floor(Math.random()*4)];
            container.appendChild(particle);
        }
    }
    createParticles();

    // ===== MAIN APP LOGIC =====
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    const uploadStatus = document.getElementById('uploadStatus');
    const queryInput = document.getElementById('queryInput');
    const queryBtn = document.getElementById('queryBtn');
    const responseArea = document.getElementById('responseArea');
    const answerText = document.getElementById('answerText');
    const avgRelevance = document.getElementById('avgRelevance');
    const relevanceProgress = document.getElementById('relevanceProgress');
    const chunksArea = document.getElementById('chunksArea');
    const healingActions = document.getElementById('healingActions');
    const resetBtn = document.getElementById('resetBtn');

    // Chart setup
    const ctx = document.getElementById('metricsChart').getContext('2d');
    let metricsChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Avg Relevance',
                data: [],
                borderColor: '#a18cd1',
                backgroundColor: 'rgba(161, 140, 209, 0.2)',
                tension: 0.4,
                pointBackgroundColor: '#f093fb',
                pointRadius: 4
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { labels: { color: '#ccc' } }
            },
            scales: {
                x: { ticks: { color: '#aaa' }, grid: { color: 'rgba(255,255,255,0.1)' } },
                y: { min: 0, max: 1, ticks: { color: '#aaa' }, grid: { color: 'rgba(255,255,255,0.1)' } }
            }
        }
    });

    async function updateMetricsChart() {
        try {
            const res = await fetch('/metrics');
            const data = await res.json();
            if (data.history.length === 0) return;
            const last10 = data.history.slice(-10);
            metricsChart.data.labels = last10.map((_, i) => `Q${data.history.length - last10.length + i + 1}`);
            metricsChart.data.datasets[0].data = last10.map(m => m.avg_relevance);
            metricsChart.update();
        } catch (e) {
            console.error('Metrics fetch error:', e);
        }
    }

    function updateHealingLog(actions) {
        if (!actions || actions.length === 0) {
            healingActions.innerHTML = '<p>No healing actions yet.</p>';
            return;
        }
        let html = '';
        actions.forEach(a => {
            html += `<div class="log-entry">
                <strong>${a.action}</strong> <span style="color:#aaa;font-size:0.8rem;">${new Date(a.timestamp).toLocaleTimeString()}</span><br>
                ${a.reason}<br>
                ${JSON.stringify(a.details)}
            </div>`;
        });
        healingActions.innerHTML = html;
    }

    // Upload handling
    uploadArea.addEventListener('click', () => fileInput.click());
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.style.borderColor = '#a18cd1';
    });
    uploadArea.addEventListener('dragleave', () => {
        uploadArea.style.borderColor = 'rgba(255,255,255,0.3)';
    });
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.style.borderColor = 'rgba(255,255,255,0.3)';
        const files = e.dataTransfer.files;
        if (files.length) {
            fileInput.files = files;
            uploadFile(files[0]);
        }
    });
    fileInput.addEventListener('change', () => {
        if (fileInput.files.length) {
            uploadFile(fileInput.files[0]);
        }
    });

    async function uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);
        uploadStatus.textContent = 'Uploading...';
        try {
            const res = await fetch('/upload', {
                method: 'POST',
                body: formData
            });
            const data = await res.json();
            uploadStatus.innerHTML = `✅ <span style="color:#a8e6cf;">${data.message} (${data.num_chunks} chunks)</span>`;
        } catch (err) {
            uploadStatus.innerHTML = `❌ <span style="color:#ff8b8b;">Upload failed: ${err.message}</span>`;
        }
    }

    // Reset knowledge base
    resetBtn.addEventListener('click', async () => {
        if (!confirm('This will delete all uploaded documents and embeddings. Continue?')) return;
        resetBtn.disabled = true;
        resetBtn.textContent = '⏳ Resetting...';
        try {
            const res = await fetch('/reset', { method: 'POST' });
            const data = await res.json();
            uploadStatus.innerHTML = `✅ <span style="color:#a8e6cf;">${data.message}</span>`;
            responseArea.classList.add('hidden');
            healingActions.innerHTML = '<p>No healing actions yet.</p>';
            updateMetricsChart();
        } catch (err) {
            uploadStatus.innerHTML = `❌ <span style="color:#ff8b8b;">Reset failed: ${err.message}</span>`;
        } finally {
            resetBtn.disabled = false;
            resetBtn.textContent = '🗑️ Reset Knowledge Base';
        }
    });

    // Query handling
    queryBtn.addEventListener('click', sendQuery);
    queryInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendQuery();
    });

    async function sendQuery() {
        const query = queryInput.value.trim();
        if (!query) return;
        queryBtn.disabled = true;
        queryBtn.textContent = '⏳ Processing...';
        responseArea.classList.add('hidden');
        try {
            const res = await fetch('/query', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query })
            });
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            const data = await res.json();

            answerText.textContent = data.answer;
            const avg = data.avg_relevance.toFixed(3);
            avgRelevance.textContent = avg;
            relevanceProgress.style.width = `${Math.min(avg * 100, 100)}%`;
            if (avg < data.threshold) {
                relevanceProgress.style.background = 'linear-gradient(to right, #f5576c, #f093fb)';
            } else {
                relevanceProgress.style.background = 'linear-gradient(to right, #43e97b, #38f9d7)';
            }

            let chunksHtml = '<h4 style="margin-top:1rem;">Retrieved Chunks</h4>';
            data.retrieved_chunks.forEach((chunk, i) => {
                chunksHtml += `<div class="chunk-item">
                    <span class="score">#${i+1} (sim: ${chunk.score.toFixed(3)}, rel: ${chunk.relevance ? chunk.relevance.toFixed(3) : 'N/A'})</span>
                    <p>${chunk.text}</p>
                </div>`;
            });
            chunksArea.innerHTML = chunksHtml;

            responseArea.classList.remove('hidden');

            if (data.healing_actions && data.healing_actions.length) {
                updateHealingLog(data.healing_actions);
            }

            await updateMetricsChart();
        } catch (err) {
            answerText.textContent = `Error: ${err.message}`;
            responseArea.classList.remove('hidden');
        } finally {
            queryBtn.disabled = false;
            queryBtn.textContent = '🔍 Ask';
        }
    }

    updateMetricsChart();
});