import requests
import re
import os
import json
import subprocess
from datetime import datetime, timedelta


def _fetch_snap_metrics():
    """Fetch metrics data via snapcraft, using already-sourced env credentials."""
    api_key = os.environ["SNAP_METRICS_KEY"]

    end_date = datetime.now() - timedelta(
        days=1
    )  # Use yesterday to avoid incomplete data
    start_date = end_date - timedelta(days=90)

    cmd = [
        "snapcraft",
        "metrics",
        "immich-distribution",
        "--name",
        "installed_base_by_version",
        "--start",
        start_date.strftime("%Y-%m-%d"),
        "--end",
        end_date.strftime("%Y-%m-%d"),
        "--format",
        "json",
    ]

    try:
        env = os.environ.copy()
        env["SNAPCRAFT_STORE_CREDENTIALS"] = api_key

        result = subprocess.run(
            cmd, env=env, capture_output=True, text=True, timeout=30
        )

        if result.returncode != 0:
            return f"<p>Error running snapcraft command: {result.stderr}</p>"

        try:
            data = json.loads(result.stdout)
            return data
        except json.JSONDecodeError as e:
            return f"<p>Error parsing JSON output: {str(e)}</p>"

    except subprocess.TimeoutExpired:
        return f"<p>Error: snapcraft command timed out</p>"
    except FileNotFoundError:
        return f"<p>Error: snapcraft command not found. Please install snapcraft.</p>"
    except Exception as e:
        return f"<p>Error: {str(e)}</p>"


def _build_metrics_chart(metrics_data):
    """Build a CSS-only chart showing metrics trends over time."""
    if isinstance(metrics_data, str):
        return metrics_data

    if not metrics_data:
        return "<p>No metrics data available</p>"

    metric = None
    if "metrics" in metrics_data and metrics_data["metrics"]:
        metric = metrics_data["metrics"][0]
    elif "metric_name" in metrics_data:
        metric = metrics_data
    else:
        return "<p>Unexpected metrics data format</p>"

    if not metric or metric.get("status") != "OK":
        return "<p>No valid metrics data available</p>"

    buckets = metric.get("buckets", [])
    series = metric.get("series", [])

    if not buckets or not series:
        return "<p>No metrics data in response</p>"

    max_value = 0
    for s in series:
        values = s.get("values", [])
        for v in values:
            if v is not None and v > max_value:
                max_value = v

    if max_value == 0:
        return "<p>No valid data points found</p>"

    def get_version_color(index):
        colors = [
            "#28a745",
            "#17a2b8",
            "#ffc107",
            "#dc3545",
            "#6f42c1",
            "#fd7e14",
            "#20c997",
            "#e83e8c",
        ]
        return colors[index % len(colors)]

    display_buckets = buckets
    start_index = 0

    # Filter out days with no data at the end
    # Find the last day that has actual data across any version
    last_data_index = -1
    for i in range(len(display_buckets) - 1, -1, -1):
        actual_index = start_index + i
        has_data = False
        for s in series:
            values = s.get("values", [])
            if actual_index < len(values) and values[actual_index] is not None:
                has_data = True
                break
        if has_data:
            last_data_index = i
            break

    # Trim display_buckets to only include days with data
    if last_data_index >= 0:
        display_buckets = display_buckets[: last_data_index + 1]
        print(f"DEBUG: After filtering, displaying {len(display_buckets)} days")
        print(
            f"DEBUG: Display range from {display_buckets[0] if display_buckets else 'N/A'} to {display_buckets[-1] if display_buckets else 'N/A'}"
        )
    else:
        print("DEBUG: No data found in any buckets")
        return "<p>No data available for the selected period</p>"

    chart_html = """
<div class="metrics-chart">
    <h3>Snap Installs by Version Over Time</h3>
    <div class="chart-container">
        <div class="chart-legend">
"""

    version_latest_values = []
    for s in series:
        version_name = s.get("name", "")
        values = s.get("values", [])
        latest_value = None
        for i in range(len(values) - 1, -1, -1):
            if i < len(values) and values[i] is not None:
                latest_value = values[i]
                break
        if latest_value is not None:
            version_latest_values.append((version_name, latest_value))

    significant_versions = set()

    for i, bucket in enumerate(buckets):
        daily_total = 0
        daily_values = {}

        for s in series:
            version_name = s.get("name", "")
            values = s.get("values", [])
            if i < len(values) and values[i] is not None:
                value = values[i]
                daily_values[version_name] = value
                daily_total += value

        # Check which versions have >1% on this day
        threshold = daily_total * 0.01
        for version_name, value in daily_values.items():
            if value >= threshold:
                significant_versions.add(version_name)

    # Sort by total installs to get consistent ordering
    version_totals = {}
    for s in series:
        version_name = s.get("name", "")
        values = s.get("values", [])
        total = sum(v for v in values if v is not None)
        version_totals[version_name] = total

    # Get significant versions sorted by total installs, limit to 9 for legend space
    major_versions = sorted(
        [v for v in significant_versions],
        key=lambda x: version_totals.get(x, 0),
        reverse=True,
    )[:9]
    display_version_names = major_versions + ["Other"]

    for i, version_name in enumerate(display_version_names):
        color = get_version_color(i)
        chart_html += f'<div class="legend-item"><span class="legend-color" style="background-color: {color};"></span>{version_name}</div>'

    chart_html += """
        </div>
        <div class="chart-grid">
"""

    for i, bucket in enumerate(display_buckets):
        chart_html += f'<div class="time-column" data-date="{bucket}">'

        # Calculate total for this day and determine 1% threshold
        period_total = 0
        all_period_values = {}

        # First pass: collect all values for this day
        for s in series:
            version_name = s.get("name", "")
            values = s.get("values", [])
            actual_index = start_index + i
            if actual_index < len(values) and values[actual_index] is not None:
                value = values[actual_index]
                all_period_values[version_name] = value
                period_total += value

        threshold_1_percent = period_total * 0.01

        # Separate major versions (>=1%) from minor versions (<1%) for this day
        period_values = {}
        period_other_total = 0

        for version_name, value in all_period_values.items():
            if value >= threshold_1_percent and version_name in major_versions:
                # This version has >=1% on this day AND is one we show individually
                period_values[version_name] = value
            else:
                # This version has <1% on this day OR is not in our top significant versions, add to "Other"
                period_other_total += value

        # Add "Other" if there are minor versions for this day
        if period_other_total > 0:
            period_values["Other"] = period_other_total

        # Generate bars with percentage tooltips
        for j, version_name in enumerate(display_version_names):
            if version_name in period_values:
                value = period_values[version_name]
                height_percent = round((value / max_value) * 100, 1)
                percentage_of_total = (
                    round((value / period_total) * 100, 1) if period_total > 0 else 0
                )
                color_index = display_version_names.index(version_name)
                color = get_version_color(color_index)

                chart_html += f"""
                <div class="bar version-{j+1}" 
                     style="height: {height_percent}%; background-color: {color};" 
                     title="{version_name}: {percentage_of_total}% on {bucket}">
                </div>"""

        chart_html += "</div>"

    chart_html += """
        </div>
    </div>
</div>
"""

    return chart_html


def _build_combined_version_pie_charts(data=None):
    """Build side-by-side pie charts showing latest version and stable version adoption"""
    if data is None:
        data = _fetch_snap_metrics()

    if isinstance(data, str):
        return data

    if not data:
        return "<p>No metrics data available</p>"

    metric = None
    if "metrics" in data and data["metrics"]:
        metric = data["metrics"][0]
    elif "metric_name" in data:
        metric = data
    else:
        return "<p>Unexpected metrics data format</p>"

    if not metric or metric.get("status") != "OK":
        return "<p>No valid metrics data available</p>"

    buckets = metric.get("buckets", [])
    series = metric.get("series", [])

    if not buckets or not series:
        return "<p>No metrics data for pie chart</p>"

    # Get the latest version by finding the version with the highest version number
    latest_version = None
    latest_version_tuple = (0, 0, 0)

    for s in series:
        version_name = s.get("name", "")
        if version_name:
            try:
                version_str = version_name.lstrip("v")
                parts = version_str.split(".")
                if len(parts) >= 3:
                    version_tuple = tuple(int(p) for p in parts[:3])
                    if version_tuple > latest_version_tuple:
                        latest_version_tuple = version_tuple
                        latest_version = version_name
            except (ValueError, IndexError):
                continue

    # Get the latest stable version from snap store API
    latest_stable_version = None
    try:
        import requests

        api_url = "https://api.snapcraft.io/v2/snaps/info/immich-distribution"
        headers = {"Snap-Device-Series": "16"}
        response = requests.get(api_url, headers=headers, timeout=5)

        if response.status_code == 200:
            channel_map = response.json().get("channel-map", [])
            latest_rev = None

            for channel_info in channel_map:
                if channel_info["channel"]["name"] in ("latest/stable", "stable"):
                    rev = channel_info["revision"]
                    if latest_rev is None or rev > latest_rev:
                        latest_rev = rev
                        latest_stable_version = channel_info["version"]
    except Exception:
        pass

    if not latest_version and not latest_stable_version:
        return "<p>Could not determine latest versions</p>"

    latest_day_values = {}
    latest_day_total = 0

    for s in series:
        version_name = s.get("name", "")
        values = s.get("values", [])

        latest_value = None
        for i in range(len(values) - 1, -1, -1):
            if i < len(values) and values[i] is not None:
                latest_value = values[i]
                break

        if latest_value is not None:
            latest_day_values[version_name] = latest_value
            latest_day_total += latest_value

    if latest_day_total == 0:
        return "<p>No data available for latest day</p>"

    latest_version_installs = (
        latest_day_values.get(latest_version, 0) if latest_version else 0
    )
    latest_version_percentage = (
        (latest_version_installs / latest_day_total * 100)
        if latest_day_total > 0
        else 0
    )
    latest_other_percentage = 100 - latest_version_percentage

    stable_version_installs = (
        latest_day_values.get(latest_stable_version, 0) if latest_stable_version else 0
    )
    stable_version_percentage = (
        (stable_version_installs / latest_day_total * 100)
        if latest_day_total > 0
        else 0
    )
    stable_other_percentage = 100 - stable_version_percentage

    combined_html = f"""
<div class="combined-pie-charts">
    <div class="pie-chart-container">
        <h3>Latest Version Adoption ({latest_version or 'N/A'})</h3>
        <div class="pie-chart latest-version" data-percentage="{latest_version_percentage:.1f}%" style="--percentage: {latest_version_percentage:.1f}">
        </div>
        <div class="pie-legend">
            <div class="pie-legend-item">
                <span class="pie-legend-color latest-version-color"></span>
                {latest_version or 'N/A'}: {latest_version_percentage:.1f}%
            </div>
            <div class="pie-legend-item">
                <span class="pie-legend-color other-versions-color"></span>
                Other versions: {latest_other_percentage:.1f}%
            </div>
        </div>
    </div>
    
    <div class="pie-chart-container">
        <h3>Latest Stable Version Adoption ({latest_stable_version or 'N/A'})</h3>
        <div class="pie-chart stable-version" data-percentage="{stable_version_percentage:.1f}%" style="--percentage: {stable_version_percentage:.1f}">
        </div>
        <div class="pie-legend">
            <div class="pie-legend-item">
                <span class="pie-legend-color stable-version-color"></span>
                {latest_stable_version or 'N/A'} (stable): {stable_version_percentage:.1f}%
            </div>
            <div class="pie-legend-item">
                <span class="pie-legend-color other-versions-color"></span>
                Other versions: {stable_other_percentage:.1f}%
            </div>
        </div>
    </div>
</div>
"""

    return combined_html


def on_page_content(html, page, config, files):
    """MkDocs hook to replace metrics macros with actual data."""
    if not re.search(r"{{[^}]+}}", html):
        return html

    macros = {
        "{{snapstore_metrics_chart}}": lambda data: _build_metrics_chart(data),
        "{{combined_version_pie_charts}}": lambda data: _build_combined_version_pie_charts(
            data
        ),
    }

    needed = [m for m in macros if m in html]
    if not needed:
        return html

    try:
        data = _fetch_snap_metrics()
    except Exception as e:
        for m in needed:
            html = html.replace(m, f"<p>Error fetching metrics: {e}</p>")
        return html

    if isinstance(data, str):
        for m in needed:
            html = html.replace(m, data)
        return html

    for m in needed:
        html = html.replace(m, macros[m](data))

    return html
