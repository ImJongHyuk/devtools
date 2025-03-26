import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys
from datetime import datetime

def load_json_data(filename):
    try:
        with open(filename, 'r') as f:
            records = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON format: {e}")
        sys.exit(1)

    if isinstance(records, dict):
        if 'timestamp' in records and 'cpu_usage' in records:
            records = [records]
        elif 'data' in records and isinstance(records['data'], list):
            records = records['data']
        else:
            print("JSON must be a list of timestamped CPU usage records.")
            sys.exit(1)

    if not isinstance(records, list):
        print("JSON must be a list of timestamped CPU usage records.")
        sys.exit(1)

    for i, record in enumerate(records):
        if not isinstance(record, dict) or 'timestamp' not in record or 'cpu_usage' not in record:
            print(f"Invalid record format at index {i}: missing 'timestamp' or 'cpu_usage'.")
            sys.exit(1)

    return records

def parse_records(records):
    df_list = []
    for record in records:
        timestamp = record['timestamp']
        for cpu in record['cpu_usage']:
            df_list.append({
                'timestamp': timestamp,
                'cpu': int(cpu['cpu']),
                'usr': cpu['usr'],
                'sys': cpu['sys'],
                'idle': cpu['idle']
            })
    df = pd.DataFrame(df_list)
    df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
    return df.sort_values(by=['timestamp', 'cpu'])

def filter_by_time(df, start_str, end_str):
    if start_str:
        start = pd.to_datetime(start_str, utc=True)
        df = df[df['timestamp'] >= start]
    if end_str:
        end = pd.to_datetime(end_str, utc=True)
        df = df[df['timestamp'] <= end]
    return df

def save_line_plot(df, output_path):
    pivot = df.pivot(index='timestamp', columns='cpu', values='usr')
    plt.figure(figsize=(2048, 512))
    pivot.plot(legend=False)
    plt.title("CPU User Usage per Core Over Time")
    plt.xlabel("Timestamp")
    plt.ylabel("User (%)")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

def save_heatmap(df, output_path):
    pivot = df.pivot(index='cpu', columns='timestamp', values='usr')
    plt.figure(figsize=(200, 100))
    sns.heatmap(pivot, cmap='viridis')
    plt.title("CPU User Usage Heatmap (Core vs Time)")
    plt.xlabel("Timestamp")
    plt.ylabel("CPU Core")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

def main():
    if len(sys.argv) < 2:
        print("Usage: python cpu_plot.py <cpu_data.json> [--start 2025-03-25T16:00:00] [--end 2025-03-25T16:30:00]")
        sys.exit(1)

    input_filename = sys.argv[1]
    start_time = None
    end_time = None

    for i in range(2, len(sys.argv)):
        if sys.argv[i] == '--start' and i + 1 < len(sys.argv):
            start_time = sys.argv[i + 1]
        elif sys.argv[i] == '--end' and i + 1 < len(sys.argv):
            end_time = sys.argv[i + 1]

    if not os.path.exists(input_filename):
        print(f"File '{input_filename}' does not exist.")
        sys.exit(1)

    base_name = os.path.splitext(os.path.basename(input_filename))[0]
    line_plot_file = f"{base_name}_line_plot.png"
    heatmap_file = f"{base_name}_heatmap.png"

    records = load_json_data(input_filename)
    df = parse_records(records)
    df = filter_by_time(df, start_time, end_time)

    if df.empty:
        print("No data available in the specified time range.")
        sys.exit(0)

    save_line_plot(df, line_plot_file)
    save_heatmap(df, heatmap_file)

    print(f"Saved: {line_plot_file}, {heatmap_file}")

if __name__ == "__main__":
    main()