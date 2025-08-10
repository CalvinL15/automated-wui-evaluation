#!/bin/bash

for arg in "$@"
do
    case $arg in
        metrics=*)
        metrics="${arg#*=}"
        ;;
        requests=*)
        requests="${arg#*=}"
        ;;
        urls=*)
        input_urls="${arg#*=}"
        ;;
    esac
done

# Validate inputs
if [ -z "$metrics" ] || [ -z "$requests" ] || [ -z "$input_urls" ]; then
    echo "Usage: $0 metrics=<metrics> requests=<number of requests> urls=\"<url1>,<url2>\""
    exit 1
fi

metrics_json="[$(echo "$metrics" | sed 's/,/", "/g' | sed 's/^/"/' | sed 's/$/"/')]"

output_file="output.txt"

perform_request() {
    local url=$1
    local metrics_json=$2
    local temp_file=$3

    curl -X POST "192.168.0.100/evaluate_url_input" \
                        -H "Content-Type: application/json" \
                        -d "{\"url\": \"$url\", \"metrics\": $metrics_json}" \
                        -o /dev/null -s -w "%{time_total}" > "$temp_file"
}

url1="${input_urls%%,*}"
url2="${input_urls#*,}"

for (( i=20; i<=20+requests; i++ ))
do
  temp_file1=$(mktemp)
  temp_file2=$(mktemp)
  echo "$url1, $url2"

  # Run requests simultaneously in the background
  perform_request "$url1" "$metrics_json" "$temp_file1" &
  pid1=$!
  perform_request "$url2" "$metrics_json" "$temp_file2" &
  pid2=$!

  # Wait for both requests to finish
  wait $pid1 $pid2

  time_taken1=$(<"$temp_file1")
  time_taken2=$(<"$temp_file2")

  rm "$temp_file1" "$temp_file2"

  wait $pid1 $pid2

  total_time=$(echo "$time_taken1" "$time_taken2" | awk '{if ($1 > $2) print $1; else print $2}')

  echo "Run $i - Total time to complete both requests: $total_time s" >> "$output_file"
  sleep 1

done