let refreshTimer = 60;
let timerId = null;

document.addEventListener('DOMContentLoaded', () => {
    fetchStocks();
    startCountdown();

    document.getElementById('refresh-btn').addEventListener('click', () => {
        manualRefresh();
    });
});

function startCountdown() {
    if (timerId) clearInterval(timerId);
    refreshTimer = 60;
    updateLastUpdated();

    timerId = setInterval(() => {
        refreshTimer--;
        updateLastUpdated();
        if (refreshTimer <= 0) {
            fetchStocks();
            refreshTimer = 60;
        }
    }, 1000);
}

async function manualRefresh() {
    const btn = document.getElementById('refresh-btn');
    btn.classList.add('loading');
    btn.innerHTML = 'Refreshing...';

    try {
        await fetch('/api/refresh', { method: 'POST' });
        setTimeout(() => {
            fetchStocks();
            startCountdown();
        }, 1500);
    } catch (err) {
        console.error("Refresh failed", err);
        btn.classList.remove('loading');
    }
}

async function fetchStocks() {
    try {
        const response = await fetch('/api/stocks');
        const stocks = await response.json();
        renderStocks(stocks);
    } catch (error) {
        console.error('Error fetching stocks:', error);
    }
}

function renderStocks(stocks) {
    const list = document.getElementById('stock-list');
    const totalEl = document.getElementById('total-stocks');
    const lowEl = document.getElementById('low-stocks');

    list.innerHTML = '';
    totalEl.textContent = stocks.length;

    const lowCount = stocks.filter(s => s.is_low).length;
    lowEl.textContent = lowCount;

    stocks.forEach(stock => {
        const card = document.createElement('div');
        card.className = 'card stock-card';
        card.setAttribute('data-symbol', stock.symbol);

        const isUp = stock.change >= 0;
        const changeClass = isUp ? 'text-green' : 'text-red';
        const changeSign = isUp ? '+' : '';
        const badgeClass = stock.status.toLowerCase().replace(' ', '-');

        card.innerHTML = `
            <div class="stock-card-header" style="margin-bottom: 0.5rem;">
                <div style="flex: 1;">
                    <div class="stock-symbol" style="font-size: 1.1rem; font-weight: 800; color: #fff;">${stock.symbol}</div>
                    <span class="stock-name" style="font-size: 0.75rem; color: #94a3b8;">${stock.name}</span>
                </div>
                <div style="display: flex; flex-direction: column; align-items: flex-end; gap: 0.25rem;">
                    <span class="badge ${badgeClass}" style="font-size: 0.65rem;">${stock.status}</span>
                </div>
            </div>
            
            <div style="display: flex; justify-content: space-between; align-items: center; margin: 1rem 0;">
                <div>
                    <span class="current-price" style="font-size: 1.5rem; font-weight: 700;">₹${stock.price.toFixed(2)}</span>
                    <span class="change-percent ${changeClass}" style="display: block; margin-left: 0; font-size: 0.8rem;">
                        ${changeSign}${stock.change.toFixed(2)}%
                    </span>
                </div>
                <div class="sparkline-container" style="width: 100px; height: 40px;">
                    <canvas id="spark-${stock.symbol.replace('.', '-')}"></canvas>
                </div>
            </div>
            
            <div class="details" style="margin-top: 0.5rem; font-size: 0.7rem; color: #64748b; border-top: 1px solid rgba(255,255,255,0.05); padding-top: 0.5rem; display: flex; justify-content: space-between;">
                <span>250D Low: ₹${(stock.two_fifty_day_low || 0).toFixed(2)}</span>
                <span class="text-secondary">View Details →</span>
            </div>
        `;

        card.style.cursor = 'pointer';
        card.onclick = () => {
            window.location.href = `details.html?symbol=${stock.symbol}`;
        };

        list.appendChild(card);

        // Render sparkline
        renderSparkline(stock.symbol);
    });

    const btn = document.getElementById('refresh-btn');
    btn.innerHTML = `
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M23 4v6h-6"></path>
            <path d="M1 20v-6h6"></path>
            <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path>
        </svg>
        Refresh
    `;
    btn.classList.remove('loading');
}

async function renderSparkline(symbol) {
    try {
        const res = await fetch(`/api/history/${symbol}?period=5d&interval=60m`);
        const history = await res.json();
        if (history.length === 0) return;

        const canvasId = `spark-${symbol.replace('.', '-')}`;
        const canvas = document.getElementById(canvasId);
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        const prices = history.map(h => h.close);
        const isUp = prices[prices.length - 1] >= prices[0];

        new Chart(ctx, {
            type: 'line',
            data: {
                labels: prices.map((_, i) => i),
                datasets: [{
                    data: prices,
                    borderColor: isUp ? '#10b981' : '#ef4444',
                    borderWidth: 1.5,
                    fill: false,
                    tension: 0.4,
                    pointRadius: 0
                }]
            },
            options: {
                plugins: { legend: { display: false }, tooltip: { enabled: false } },
                scales: { x: { display: false }, y: { display: false } },
                responsive: true,
                maintainAspectRatio: false
            }
        });
    } catch (e) {
        console.error("Sparkline error", e);
    }
}

function updateLastUpdated() {
    const el = document.getElementById('last-updated');
    el.innerHTML = `Next update in <span style="color: var(--accent-green); font-weight: 700;">${refreshTimer}s</span>`;
}
