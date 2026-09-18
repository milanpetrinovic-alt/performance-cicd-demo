import json
from pathlib import Path


BASE_DIR = Path(__file__).parent
SUMMARY_FILE = BASE_DIR / "summary.json"
REPORT_FILE = BASE_DIR / "performance-report.html"


with SUMMARY_FILE.open(encoding="utf-8") as file:
    data = json.load(file)


metrics = data["metrics"]

duration = metrics["http_req_duration"]
failed = metrics["http_req_failed"]
checks = metrics["checks"]
requests = metrics["http_reqs"]


p95 = duration["p(95)"]
average = duration["avg"]
maximum = duration["max"]

error_rate = failed["value"] * 100
check_rate = checks["value"] * 100
request_count = requests["count"]


duration_thresholds = duration.get("thresholds", {})
error_thresholds = failed.get("thresholds", {})

duration_threshold_text = next(iter(duration_thresholds), "N/A")
error_threshold_text = next(iter(error_thresholds), "N/A")


# In this k6 summary format:
# False = threshold was not crossed -> PASS
# True = threshold was crossed -> FAIL
duration_passed = not any(duration_thresholds.values())
error_passed = not any(error_thresholds.values())

overall_passed = duration_passed and error_passed

status = "PASS" if overall_passed else "FAIL"
status_class = "pass" if overall_passed else "fail"


html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Performance Test Report</title>

    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 900px;
            margin: 40px auto;
            padding: 0 20px;
        }}

        h1 {{
            margin-bottom: 5px;
        }}

        .status {{
            font-size: 28px;
            font-weight: bold;
            margin: 20px 0;
        }}

        .pass {{
            color: green;
        }}

        .fail {{
            color: red;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 25px;
        }}

        th, td {{
            padding: 12px;
            border-bottom: 1px solid #ddd;
            text-align: left;
        }}

        th {{
            background: #f5f5f5;
        }}
    </style>
</head>

<body>

<h1>Performance Test Report</h1>

<div class="status {status_class}">
    {status}
</div>

<table>
    <tr>
        <th>Metric</th>
        <th>Result</th>
        <th>Threshold</th>
        <th>Status</th>
    </tr>

    <tr>
        <td>P95 Response Time</td>
        <td>{p95:.2f} ms</td>
        <td>{duration_threshold_text}</td>
        <td>{"PASS" if duration_passed else "FAIL"}</td>
    </tr>

    <tr>
        <td>Error Rate</td>
        <td>{error_rate:.2f}%</td>
        <td>{error_threshold_text}</td>
        <td>{"PASS" if error_passed else "FAIL"}</td>
    </tr>

    <tr>
        <td>Checks Passed</td>
        <td>{check_rate:.2f}%</td>
        <td>-</td>
        <td>-</td>
    </tr>
</table>

<h2>Additional Metrics</h2>

<table>
    <tr>
        <td>Average Response Time</td>
        <td>{average:.2f} ms</td>
    </tr>

    <tr>
        <td>Maximum Response Time</td>
        <td>{maximum:.2f} ms</td>
    </tr>

    <tr>
        <td>Total Requests</td>
        <td>{request_count}</td>
    </tr>
</table>

</body>
</html>
"""


REPORT_FILE.write_text(html, encoding="utf-8")

print(f"Performance report generated: {REPORT_FILE}")