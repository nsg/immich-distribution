#!/bin/bash
set -e

STATHOST_URL="${STATHOST_URL:-https://static.nsg.cc}"
BUCKET="immich-distribution"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPORT_DIR="${1:-$SCRIPT_DIR/report}"
VIDEO_DIR="${2:-$SCRIPT_DIR/test-results/videos}"

if [ -z "$STATHOST_TOKEN" ]; then
    echo "Error: STATHOST_TOKEN environment variable not set"
    exit 1
fi

RUN_ID="${GITHUB_RUN_ID:-$(date +%s)}"
JOB_NAME="${GITHUB_JOB:-local}"
JOB_NAME_SAFE=$(echo "$JOB_NAME" | tr ' ' '-' | tr -cd '[:alnum:]-_')
UPLOAD_PATH="runs/${RUN_ID}/${JOB_NAME_SAFE}"

upload_file() {
    local file="$1"
    local remote_path="$2"
    
    if ! curl -sf -X PUT \
        -H "Authorization: Bearer $STATHOST_TOKEN" \
        --data-binary "@$file" \
        "${STATHOST_URL}/${BUCKET}/${remote_path}"; then
        echo "Warning: Failed to upload $file"
        return 1
    fi
}

echo "Uploading test report to ${STATHOST_URL}/${BUCKET}/${UPLOAD_PATH}"
echo ""

if [ -d "$REPORT_DIR" ]; then
    echo "Uploading report files..."
    find "$REPORT_DIR" -type f | while read -r file; do
        relative_path="${file#$REPORT_DIR/}"
        echo "  $relative_path"
        upload_file "$file" "${UPLOAD_PATH}/report/${relative_path}"
    done
else
    echo "Warning: Report directory not found: $REPORT_DIR"
fi

if [ -d "$VIDEO_DIR" ]; then
    video_count=$(find "$VIDEO_DIR" -type f -name "*.webm" 2>/dev/null | wc -l)
    if [ "$video_count" -gt 0 ]; then
        echo ""
        echo "Uploading $video_count video(s)..."
        find "$VIDEO_DIR" -type f -name "*.webm" | while read -r file; do
            filename=$(basename "$file")
            echo "  $filename"
            upload_file "$file" "${UPLOAD_PATH}/videos/${filename}"
        done
    fi
fi

generate_index() {
    local temp_file
    temp_file=$(mktemp)
    
    cat > "$temp_file" << HTMLEOF
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Test Results - Run ${RUN_ID} - ${JOB_NAME}</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; background: #f5f5f5; }
        h1 { color: #333; }
        .meta { color: #666; margin-bottom: 20px; }
        .section { background: white; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .section h2 { margin-top: 0; color: #444; }
        a { color: #0066cc; text-decoration: none; }
        a:hover { text-decoration: underline; }
        .video-list { list-style: none; padding: 0; }
        .video-list li { padding: 10px 0; border-bottom: 1px solid #eee; }
        .video-list li:last-child { border-bottom: none; }
        video { max-width: 100%; margin-top: 10px; border-radius: 4px; }
        .video-container { margin: 15px 0; }
        .video-name { font-weight: 500; }
    </style>
</head>
<body>
    <h1>Test Results</h1>
    <div class="meta">
        <p>Run ID: ${RUN_ID} | Job: ${JOB_NAME}</p>
        <p>Generated: $(date -u '+%Y-%m-%d %H:%M:%S UTC')</p>
    </div>
    
    <div class="section">
        <h2>📊 Test Report</h2>
        <p><a href="report/index.html">View detailed pytest-html report →</a></p>
    </div>
HTMLEOF

    if [ -d "$VIDEO_DIR" ] && [ -n "$(find "$VIDEO_DIR" -name "*.webm" 2>/dev/null)" ]; then
        cat >> "$temp_file" << 'VIDEOHEADER'
    
    <div class="section">
        <h2>🎬 Test Videos</h2>
VIDEOHEADER
        
        for video in "$VIDEO_DIR"/*.webm; do
            [ -f "$video" ] || continue
            video_name=$(basename "$video")
            cat >> "$temp_file" << VIDEOITEM
        <div class="video-container">
            <div class="video-name">${video_name}</div>
            <video controls preload="metadata">
                <source src="videos/${video_name}" type="video/webm">
                Your browser does not support the video tag.
            </video>
        </div>
VIDEOITEM
        done
        
        echo "    </div>" >> "$temp_file"
    fi

    cat >> "$temp_file" << 'HTMLFOOTER'
</body>
</html>
HTMLFOOTER

    echo "$temp_file"
}

echo ""
echo "Generating index page..."
INDEX_FILE=$(generate_index)
upload_file "$INDEX_FILE" "${UPLOAD_PATH}/index.html"
rm -f "$INDEX_FILE"

update_root_index() {
    echo "Updating root index..."
    
    local file_list
    file_list=$(curl -sf -H "Authorization: Bearer $STATHOST_TOKEN" \
        "${STATHOST_URL}/${BUCKET}/_meta/list" 2>/dev/null || echo "[]")
    
    local temp_file
    temp_file=$(mktemp)
    
    cat > "$temp_file" << 'HTMLHEAD'
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Immich Distribution - Test Reports</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 900px; margin: 0 auto; padding: 20px; background: #f5f5f5; }
        h1 { color: #333; }
        .description { color: #666; margin-bottom: 30px; }
        .run-list { background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); overflow: hidden; }
        .run-item { display: block; padding: 15px 20px; border-bottom: 1px solid #eee; color: #333; text-decoration: none; transition: background 0.2s; }
        .run-item:last-child { border-bottom: none; }
        .run-item:hover { background: #f8f9fa; }
        .run-id { font-weight: 600; color: #0066cc; }
        .run-job { color: #666; font-size: 0.9em; margin-left: 10px; }
        .empty { padding: 40px; text-align: center; color: #666; }
    </style>
</head>
<body>
    <h1>🧪 Immich Distribution Test Reports</h1>
    <p class="description">Test reports from failed CI runs. Each report includes detailed pytest results and video recordings.</p>
    <div class="run-list">
HTMLHEAD

    local has_runs=false
    echo "$file_list" | tr -d '[]"' | tr ',' '\n' | grep "runs/.*index.html" | sort -r | head -50 | while read -r path; do
        [ -z "$path" ] && continue
        has_runs=true
        run_path=$(dirname "$path")
        run_id=$(echo "$run_path" | cut -d'/' -f2)
        job_name=$(echo "$run_path" | cut -d'/' -f3-)
        cat >> "$temp_file" << RUNITEM
        <a class="run-item" href="${run_path}/">
            <span class="run-id">Run #${run_id}</span>
            <span class="run-job">${job_name}</span>
        </a>
RUNITEM
    done
    
    if ! grep -q "run-item" "$temp_file"; then
        echo '        <div class="empty">No test reports yet.</div>' >> "$temp_file"
    fi

    cat >> "$temp_file" << 'HTMLFOOT'
    </div>
</body>
</html>
HTMLFOOT

    upload_file "$temp_file" "index.html"
    rm -f "$temp_file"
}

update_root_index

REPORT_URL="${STATHOST_URL}/${BUCKET}/${UPLOAD_PATH}/"
echo ""
echo "==========================================="
echo "Test results available at:"
echo "$REPORT_URL"
echo "==========================================="

if [ -n "$GITHUB_STEP_SUMMARY" ]; then
    {
        echo "## 📊 Test Report"
        echo ""
        echo "**[View Test Results](${REPORT_URL})**"
        echo ""
        echo "- [Detailed pytest-html Report](${REPORT_URL}report/index.html)"
        echo ""
        if [ -d "$VIDEO_DIR" ] && [ -n "$(find "$VIDEO_DIR" -name "*.webm" 2>/dev/null)" ]; then
            echo "### 🎬 Test Videos"
            echo ""
            for video in "$VIDEO_DIR"/*.webm; do
                [ -f "$video" ] || continue
                video_name=$(basename "$video")
                echo "- [${video_name}](${REPORT_URL}videos/${video_name})"
            done
        fi
    } >> "$GITHUB_STEP_SUMMARY"
fi
