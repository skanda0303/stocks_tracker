document.addEventListener('DOMContentLoaded', () => {
    fetchStocks();

    // Auto refresh every 60 seconds
    setInterval(fetchStocks, 60000);

    document.getElementById('refresh-btn').addEventListener('click', () => {
        const btn = document.getElementById('refresh-btn');
        btn.classList.add('loading');
        btn.innerHTML = 'Refreshing...';

        // Trigger backend refresh
        fetch('/api/refresh', { method: 'POST' })
            .then(() => {
                setTimeout(fetchStocks, 2000); // Wait a bit for backend to fetch
            })
            .catch(err => console.error("Refresh failed", err));
    });
});

async function fetchStocks() {
    try {
        const response = await fetch('/api/stocks');
        const stocks = await response.json();
        renderStocks(stocks);
        updateLastUpdated();
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

    console.log("Rendering stocks version 1.2");
    stocks.forEach(stock => {
        const card = document.createElement('div');
        card.className = 'card stock-card';

        const isUp = stock.change >= 0;
        const changeClass = isUp ? 'text-green' : 'text-red';
        const changeSign = isUp ? '+' : '';
        const badgeClass = stock.status.toLowerCase();

        card.innerHTML = `
            <div class="stock-card-header" style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem;">
                <div style="flex: 1;">
                    <div class="stock-symbol" style="font-size: 1.2rem; font-weight: 800; color: #fff;">${stock.symbol}</div>
                    <span class="stock-name" style="font-size: 0.8rem; color: #94a3b8;">${stock.name}</span>
                </div>
                <div style="display: flex; flex-direction: column; align-items: flex-end; gap: 0.5rem;">
                    <span class="badge ${badgeClass}" style="margin-bottom: 2px;">${stock.status}</span>
                    <div class="box-stat-avg" style="background: rgba(30, 41, 59, 1); border: 1px solid rgba(255,255,255,0.1); padding: 4px 8px; border-radius: 6px; min-width: 80px; text-align: right;">
                        <div style="font-size: 0.6rem; color: #64748b; text-transform: uppercase; font-weight: 700;">250D Avg</div>
                        <div style="font-size: 0.85rem; color: #e2e8f0; font-family: monospace;">₹${(stock.two_fifty_day_avg || 0).toFixed(2)}</div>
                    </div>
                </div>
            </div>
            
            <div class="price-container" style="display: flex; justify-content: space-between; align-items: flex-end; margin-top: 1rem;">
                <div>
                    <span class="current-price" style="font-size: 1.8rem; font-weight: 700;">₹${stock.price.toFixed(2)}</span>
                    <span class="change-percent ${changeClass}" style="display: block; margin-left: 0; margin-top: -4px;">
                        ${changeSign}${stock.change.toFixed(2)}%
                    </span>
                </div>
                <div class="box-stat-low" style="background: rgba(251, 191, 36, 0.1); border: 1px solid rgba(251, 191, 36, 0.4); padding: 4px 8px; border-radius: 6px; min-width: 80px; text-align: right;">
                    <div style="font-size: 0.6rem; color: #fbbf24; text-transform: uppercase; font-weight: 700;">250D Low</div>
                    <div style="font-size: 0.85rem; color: #fbbf24; font-family: monospace; font-weight: 700;">₹${(stock.two_fifty_day_low || 0).toFixed(2)}</div>
                </div>
            </div>
            
            <div class="details" style="margin-top: 1rem; font-size: 0.8rem; color: #94a3b8; border-top: 1px solid rgba(255,255,255,0.05); padding-top: 0.75rem;">
                ${stock.details}
            </div>
        `;

        // Make card clickable
        card.style.cursor = 'pointer';
        card.onclick = () => {
            window.location.href = `details.html?symbol=${stock.symbol}`;
        };

        list.appendChild(card);
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

function updateLastUpdated() {
    const now = new Date();
    document.getElementById('last-updated').textContent = `Last check: ${now.toLocaleTimeString()}`;
}
