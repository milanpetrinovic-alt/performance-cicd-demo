import json
from pathlib import Path

BASE_DIR = Path(__file__).parent
REPORT_FILE = BASE_DIR / "workload-report.html"

TARGET_RPS = 10.0

TARGET_MIX = {
    "browse": 70,
    "search": 20,
    "checkout": 10,
}

# Demo tolerances, not production performance requirements
RPS_TOLERANCE = 1.0
MIX_TOLERANCE = 3.0


def load_summary(filename):
    with (BASE_DIR / filename).open(encoding="utf-8") as file:
        data = json.load(file)

    metrics = data["metrics"]

    counts = {}
    rates = {}

    for scenario in TARGET_MIX:
        metric_name = f"{scenario}_operations"

        metric = metrics[metric_name]

        counts[scenario] = metric["count"]
        rates[scenario] = metric["rate"]

    total_count = sum(counts.values())
    total_rate = sum(rates.values())

    if total_count == 0:
        raise ValueError(f"No completed operations in {filename}")

    percentages = {
        scenario: count / total_count * 100
        for scenario, count in counts.items()
    }

    return {
        "counts": counts,
        "rates": rates,
        "total_count": total_count,
        "total_rate": total_rate,
        "percentages": percentages,
        "error_rate": metrics["http_req_failed"]["value"] * 100,
        "vus": metrics["vus_max"]["max"],
    }


naive = load_summary("naive-summary.json")
modeled = load_summary("modeled-summary.json")


def status_cell(value, target, tolerance, unit="%"):
    passed = abs(value - target) <= tolerance

    status = "on-target" if passed else "off-target"
    label = "ON TARGET" if passed else "OFF TARGET"

    return f"""
        <td class="{status}">
            <strong>{value:.2f}{unit}</strong>
            <span class="badge">{label}</span>
        </td>
    """


def traffic_bar(results):
    segments = ""

    for scenario in TARGET_MIX:
        percentage = results["percentages"][scenario]

        segments += f"""
            <div class="{scenario}"
                 style="width: {percentage:.2f}%"
                 title="{scenario}: {percentage:.2f}%">
            </div>
        """

    return f'<div class="traffic-bar">{segments}</div>'


rows = f"""
<tr>
    <td>Total Throughput</td>
    <td>{TARGET_RPS:.2f} ops/s</td>
    {status_cell(naive["total_rate"], TARGET_RPS, RPS_TOLERANCE, " ops/s")}
    {status_cell(modeled["total_rate"], TARGET_RPS, RPS_TOLERANCE, " ops/s")}
</tr>
"""

for scenario, target in TARGET_MIX.items():
    rows += f"""
    <tr>
        <td>{scenario.capitalize()}</td>
        <td>{target:.2f}%</td>
        {status_cell(naive["percentages"][scenario], target, MIX_TOLERANCE)}
        {status_cell(modeled["percentages"][scenario], target, MIX_TOLERANCE)}
    </tr>
    """


html = f"""
<!DOCTYPE html>
<html lang="en">

<head>
<meta charset="UTF-8">
<title>Workload Modeling Report</title>

<style>
    body {{
        font-family: Arial, sans-serif;
        background: #101827;
        color: #e5e7eb;
        max-width: 1100px;
        margin: 50px auto;
        padding: 0 30px;
    }}

    h1 {{
        color: white;
        margin-bottom: 8px;
    }}

    h2 {{
        margin-top: 40px;
        color: white;
    }}

    .subtitle {{
        color: #9ca3af;
        margin-bottom: 35px;
    }}

    .card {{
        background: #1e293b;
        border-radius: 12px;
        padding: 25px;
        margin-bottom: 25px;
    }}

    table {{
        width: 100%;
        border-collapse: collapse;
    }}

    th, td {{
        padding: 16px;
        text-align: left;
        border-bottom: 1px solid #334155;
    }}

    th {{
        color: #94a3b8;
        font-weight: normal;
    }}

    td {{
        font-size: 15px;
    }}

    .on-target {{
        color: #4ade80;
    }}

    .off-target {{
        color: #fb7185;
    }}

    .badge {{
        display: block;
        font-size: 10px;
        margin-top: 5px;
        letter-spacing: 1px;
    }}

    .traffic-bar {{
        display: flex;
        width: 100%;
        height: 35px;
        overflow: hidden;
        border-radius: 6px;
        margin: 12px 0 25px;
    }}

    .browse {{
        background: #38bdf8;
    }}

    .search {{
        background: #a78bfa;
    }}

    .checkout {{
        background: #fbbf24;
    }}

    .legend {{
        display: flex;
        gap: 25px;
        margin-top: 20px;
        font-size: 13px;
    }}

    .legend span::before {{
        content: "● ";
    }}

    .legend .browse-label {{
        color: #38bdf8;
    }}

    .legend .search-label {{
        color: #a78bfa;
    }}

    .legend .checkout-label {{
        color: #fbbf24;
    }}

    .note {{
        color: #94a3b8;
        font-size: 13px;
        line-height: 1.6;
    }}
</style>
</head>

<body>

<h1>Workload Modeling Report</h1>

<p class="subtitle">
Target vs. actual traffic — Naive and Calculated Models
</p>

<div class="card">

<h2>Workload Accuracy</h2>

<table>
<thead>
<tr>
    <th>Metric</th>
    <th>Business Target</th>
    <th>Naive Model</th>
    <th>Calculated Model</th>
</tr>
</thead>

<tbody>
{rows}
</tbody>
</table>

</div>

<div class="card">

<h2>Traffic Distribution</h2>

<div class="legend">
    <span class="browse-label">Browse</span>
    <span class="search-label">Search</span>
    <span class="checkout-label">Checkout</span>
</div>

<h3>Business Target — 70 / 20 / 10</h3>

<div class="traffic-bar">
    <div class="browse" style="width:70%"></div>
    <div class="search" style="width:20%"></div>
    <div class="checkout" style="width:10%"></div>
</div>

<h3>Naive Model</h3>

{traffic_bar(naive)}

<h3>Calculated Model</h3>

{traffic_bar(modeled)}

</div>

<div class="card">

<h2>Execution Details</h2>

<table>
<tr>
    <th>Metric</th>
    <th>Naive</th>
    <th>Calculated</th>
</tr>

<tr>
    <td>Virtual Users</td>
    <td>{naive["vus"]}</td>
    <td>{modeled["vus"]}</td>
</tr>

<tr>
    <td>Completed Operations</td>
    <td>{naive["total_count"]}</td>
    <td>{modeled["total_count"]}</td>
</tr>

<tr>
    <td>HTTP Error Rate</td>
    <td>{naive["error_rate"]:.2f}%</td>
    <td>{modeled["error_rate"]:.2f}%</td>
</tr>

</table>

</div>

<p class="note">
The ON TARGET / OFF TARGET labels use demo tolerances:
±1 operation/second for total throughput and ±3 percentage
points for scenario distribution. These are illustrative
workload-model checks, not application performance thresholds.
The operation counts include successful requests only.
</p>

</body>
</html>
"""

REPORT_FILE.write_text(html, encoding="utf-8")

print(f"Workload report generated: {REPORT_FILE}")