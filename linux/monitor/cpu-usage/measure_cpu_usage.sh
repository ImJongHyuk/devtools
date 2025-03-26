#!/bin/bash

logfile="cpu_usage_$(date +%Y%m%d_%H%M%S).json"

while true; do
  raw=$(mpstat -P ALL 1 1 | awk '/^[0-9]/ && $3 ~ /[0-9]+/ {print}')

  echo "{" >> $logfile
  echo "  \"timestamp\": \"$(date -Iseconds)\"," >> $logfile
  echo "  \"cpu_usage\": [" >> $logfile

  count=$(echo "$raw" | wc -l)
  i=1
  echo "$raw" | while read -r line; do
    cpu=$(echo "$line" | awk '{print $3}')
    usr=$(echo "$line" | awk '{print $4}')
    sys=$(echo "$line" | awk '{print $6}')
    idle=$(echo "$line" | awk '{print $13}')
    echo -n "    {\"cpu\": \"$cpu\", \"usr\": $usr, \"sys\": $sys, \"idle\": $idle}" >> $logfile
    if [ $i -lt $count ]; then echo "," >> $logfile; else echo "" >> $logfile; fi
    ((i++))
  done

  echo "  ]" >> $logfile
  echo "}," >> $logfile

  sleep 1
done