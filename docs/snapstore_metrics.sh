#!/usr/bin/env bash
set -euo pipefail

OUTPUT_FILE="site/snapstore-metrics.json"
CHART_FILE="site/snapstore-metrics-chart.json"

echo "Fetching snap metrics data..."

# Check if snapcraft is available and credentials are set
if ! command -v snapcraft &> /dev/null; then
    echo "Warning: snapcraft command not found. Metrics will not be available." >&2
    echo '{"error": "snapcraft not installed"}' > "$OUTPUT_FILE"
    echo '{"error": "snapcraft not installed"}' > "$CHART_FILE"
    exit 0
fi

if [ -z "${SNAPCRAFT_STORE_CREDENTIALS:-}" ] && [ -z "${SNAP_METRICS_KEY:-}" ]; then
    echo "Warning: SNAPCRAFT_STORE_CREDENTIALS or SNAP_METRICS_KEY not set. Metrics will not be available." >&2
    echo '{"error": "no credentials"}' > "$OUTPUT_FILE"
    echo '{"error": "no credentials"}' > "$CHART_FILE"
    exit 0
fi

# Set credentials if SNAP_METRICS_KEY is provided
if [ -n "${SNAP_METRICS_KEY:-}" ]; then
    export SNAPCRAFT_STORE_CREDENTIALS="$SNAP_METRICS_KEY"
fi

# Calculate date range (last 90 days, ending yesterday to avoid incomplete data)
end_date=$(date -d "yesterday" +%Y-%m-%d)
start_date=$(date -d "90 days ago" +%Y-%m-%d)

# Fetch metrics from snapcraft
if ! metrics_output=$(snapcraft metrics immich-distribution \
    --name installed_base_by_version \
    --start "$start_date" \
    --end "$end_date" \
    --format json 2>&1); then
    echo "Error fetching metrics: $metrics_output" >&2
    echo '{"error": "fetch failed"}' > "$OUTPUT_FILE"
    echo '{"error": "fetch failed"}' > "$CHART_FILE"
    exit 0
fi

# Save the raw metrics output
echo "$metrics_output" > "$OUTPUT_FILE"

# Process the metrics into chart-ready format using jq
if ! echo "$metrics_output" | jq -e '.status == "OK"' > /dev/null 2>&1; then
    echo "Warning: Metrics status not OK" >&2
    echo '{"error": "status not OK"}' > "$CHART_FILE"
    exit 0
fi

echo "$metrics_output" | jq '
{
    chart_data: (
        .buckets as $buckets |
        .series as $series |
        
        # Find max value
        ($series | map(.values | map(select(. != null))) | flatten | max) as $max_value |
        
        # Get display buckets (trim trailing empty days)
        ($buckets | length) as $total_days |
        (reduce range(0; $total_days) as $i (
            -1;
            . as $last |
            (reduce $series[] as $s (
                false;
                . or ($s.values[$total_days - 1 - $i] != null)
            )) as $has_data |
            if $has_data and $last == -1 then ($total_days - $i) else $last end
        )) as $last_index |
        
        $buckets[0:$last_index] as $display_buckets |
        
        # Find significant versions (>1% on any day)
        (reduce range(0; $display_buckets | length) as $i (
            [];
            . as $sig_versions |
            (reduce $series[] as $s (0; . + ($s.values[$i] // 0))) as $daily_total |
            ($daily_total * 0.01) as $threshold |
            (reduce $series[] as $s (
                $sig_versions;
                if ($s.values[$i] // 0) >= $threshold and ($s.name | IN($sig_versions[] | .)) | not then
                    . + [$s.name]
                else
                    .
                end
            ))
        )) as $significant_versions |
        
        # Get top 9 versions by total installs
        ($series | 
         map(select(.name | IN($significant_versions[])) | {name: .name, total: (.values | map(select(. != null)) | add)}) |
         sort_by(-.total) | 
         map(.name) | 
         .[0:9]
        ) as $major_versions |
        
        # Colors for versions
        ["#28a745", "#17a2b8", "#ffc107", "#dc3545", "#6f42c1", "#fd7e14", "#20c997", "#e83e8c"] as $colors |
        
        # Process each day
        $display_buckets | to_entries | map(
            .key as $i |
            .value as $bucket |
            
            (reduce $series[] as $s (0; . + ($s.values[$i] // 0))) as $period_total |
            ($period_total * 0.01) as $threshold |
            
            (reduce $series[] as $s (
                {bars: [], other: 0};
                ($s.values[$i] // 0) as $value |
                if $value > 0 then
                    if ($s.name | IN($major_versions[])) and $value >= $threshold then
                        ($major_versions | to_entries | map(select(.value == $s.name)) | .[0].key) as $idx |
                        .bars += [{
                            version: $s.name,
                            value: $value,
                            percentage: (if $period_total > 0 then ($value / $period_total * 100 * 10 | round / 10) else 0 end),
                            height: (if $max_value > 0 then ($value / $max_value * 100 * 10 | round / 10) else 0 end),
                            color: $colors[$idx % ($colors | length)]
                        }]
                    else
                        .other += $value
                    end
                else
                    .
                end
            )) as $day_data |
            
            {
                date: $bucket,
                bars: (
                    if $day_data.other > 0 then
                        $day_data.bars + [{
                            version: "Other",
                            value: $day_data.other,
                            percentage: (if $period_total > 0 then ($day_data.other / $period_total * 100 * 10 | round / 10) else 0 end),
                            height: (if $max_value > 0 then ($day_data.other / $max_value * 100 * 10 | round / 10) else 0 end),
                            color: "#6c757d"
                        }]
                    else
                        $day_data.bars
                    end
                )
            }
        )
    ),
    legend: (
        ["#28a745", "#17a2b8", "#ffc107", "#dc3545", "#6f42c1", "#fd7e14", "#20c997", "#e83e8c"] as $colors |
        .series as $series |
        
        # Find significant versions
        (reduce range(0; .buckets | length) as $i (
            [];
            . as $sig_versions |
            (reduce $series[] as $s (0; . + ($s.values[$i] // 0))) as $daily_total |
            ($daily_total * 0.01) as $threshold |
            (reduce $series[] as $s (
                $sig_versions;
                if ($s.values[$i] // 0) >= $threshold and ($s.name | IN($sig_versions[] | .)) | not then
                    . + [$s.name]
                else
                    .
                end
            ))
        )) as $significant_versions |
        
        # Get top 9 versions
        ($series | 
         map(select(.name | IN($significant_versions[])) | {name: .name, total: (.values | map(select(. != null)) | add)}) |
         sort_by(-.total) | 
         map(.name) | 
         .[0:9]
        ) as $major_versions |
        
        ($major_versions | to_entries | map({
            version: .value,
            color: $colors[.key % ($colors | length)]
        })) + [{version: "Other", color: "#6c757d"}]
    )
}
' > "$CHART_FILE"

echo "Wrote snap metrics data to $OUTPUT_FILE"
echo "Wrote snap metrics chart data to $CHART_FILE"
