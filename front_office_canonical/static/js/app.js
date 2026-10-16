function openTab(event, tabName) {
    var i, tabContent, tabLinks;
    tabContent = document.getElementsByClassName("tab-content");
    for (i = 0; i < tabContent.length; i++) {
        tabContent[i].classList.remove("active");
    }
    tabLinks = document.getElementsByClassName("tab-link");
    for (i = 0; i < tabLinks.length; i++) {
        tabLinks[i].classList.remove("active");
    }
    document.getElementById(tabName).classList.add("active");
    event.currentTarget.classList.add("active");

    if (tabName === 'briefing') fetchBriefing();
    if (tabName === 'ledger') fetchLedger();
    if (tabName === 'logs') fetchLogs();
}

async function fetchBriefing() {
    const resp = await fetch('/api/briefing');
    const data = await resp.json();
    document.getElementById('briefing-output').textContent = data.output || data.error;
}

async function fetchLedger() {
    const resp = await fetch('/api/ledger');
    const data = await resp.json();
    let html = '<table><thead><tr><th>PACKAGE</th><th>PLATFORM</th><th>STATUS</th><th>SCORE</th></tr></thead><tbody>';
    if (data.entries && data.entries.length > 0) {
        data.entries.forEach(e => {
            html += `<tr>
                <td>${e.package}</td>
                <td>${e.platform}</td>
                <td>${e.label}</td>
                <td>${e.score}</td>
            </tr>`;
        });
    } else {
        html += '<tr><td colspan="4">No data found. Run pipeline.</td></tr>';
    }
    html += '</tbody></table>';
    document.getElementById('ledger-data').innerHTML = html;
}

async function fetchLogs() {
    const resp = await fetch('/api/logs');
    const data = await resp.json();
    document.getElementById('logs-output').textContent = data.logs;
}

function shipIt() {
    const btn = document.getElementById('ship-button');
    const status = document.getElementById('status-indicator');

    btn.disabled = true;
    btn.style.opacity = 0.5;
    status.textContent = "STATUS: SHIPPING... PLEASE WAIT...";

    fetch('/api/ship', { method: 'POST' })
        .then(resp => resp.json())
        .then(data => {
            console.log(data);
            setTimeout(() => {
                btn.disabled = false;
                btn.style.opacity = 1;
                status.textContent = "STATUS: READY";
                fetchBriefing();
            }, 3000);
        });
}

// Initial fetch
fetchBriefing();

// Periodically update marquee or something fun
const quotes = [
    "MRS. HIGGINS IS WATCHING.",
    "NO EXCUSES. JUST SHIP.",
    "NON-FILTERED SMOKE DETECTED.",
    "MOTHBALLS INVENTORY: 98%",
    "BOLT11 INVOICES GENERATED.",
    "VOLTAGE API STATUS: NOMINAL.",
    "CLEAN UP THAT COFFEE STAIN."
];

setInterval(() => {
    const marquee = document.getElementById('marquee');
    marquee.textContent = quotes[Math.floor(Math.random() * quotes.length)];
}, 15000);
