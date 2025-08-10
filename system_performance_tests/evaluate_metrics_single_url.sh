#!/bin/bash

# metrics to be evaluated
metrics=""

# number of requests
requests=0

# url to be evaluated
url=""

# Parse command-line arguments
for arg in "$@"
do
    case $arg in
        metrics=*)
        metrics="${arg#*=}"
        shift
        ;;
        requests=*)
        requests="${arg#*=}"
        shift
        ;;
        url=*)
        url="${arg#*=}"
        shift
        ;;
        *)
        # Unknown option
        ;;
    esac
done

# Check if variables are set
if [[ -z "$metrics" || -z "$requests" || -z "$url" ]]; then
    echo "Usage: $0 metrics=<metrics> requests=<number of requests> url=\"<URL>\""
    exit 1
fi

output_file="curl_times_$(echo "$metrics" | tr ',' '_').txt"

total_time=0

metrics_json=$(echo "$metrics" | sed 's/,/","/g' | sed 's/^/["/;s/$/"]/')

# first request, not counted (init)
curl -X POST "http://localhost:8000/evaluate_url_input" \
                        -H "Content-Type: application/json" \
                        -d "{\"url\": \"$url\", \"metrics\": $metrics_json}" \
                        -o /dev/null -s -w "%{time_total}"

for ((i = 1; i <= requests; i++)); do
  time_taken=$(curl -X POST "http://localhost:8000/evaluate_url_input" \
                        -H "Content-Type: application/json" \
                        -d "{\"url\": \"$url\", \"metrics\": $metrics_json}" \
                        -o /dev/null -s -w "%{time_total}")
  echo "Attempt $i: $time_taken s" >> "$output_file"
  total_time=$(echo $total_time + "$time_taken" | bc)
  done

echo "Curl requests completed. Times recorded in $output_file."