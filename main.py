# ==========================================
# Campus Energy-Use Dashboard
# Name: Janvi Sehrawat
# Roll No.: 2501350002
# ==========================================

import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt

# ==========================================
# TASK 1: DATA INGESTION & VALIDATION
# ==========================================

def ingest_data(data_folder="data/"):
    path = Path(data_folder)
    csv_files = list(path.glob("*.csv"))

    print("CSV Files Found:", csv_files)  

    if not csv_files:
        raise FileNotFoundError("❌ No CSV files found inside the data folder!")

    all_frames = []

    for file in csv_files:
        try:
            df = pd.read_csv(file)

            if "timestamp" not in df.columns or "kwh" not in df.columns:
                print(f"⚠️ Skipping {file.name} - Missing required columns")
                continue  

            df["building"] = file.stem
            df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
            df = df.dropna(subset=["timestamp"])

            if len(df) == 0:
                print(f"⚠️ Skipping {file.name} - All timestamps invalid")
                continue

            all_frames.append(df)
            print(f"✅ Loaded: {file.name}")

        except Exception as e:
            print(f"❌ Failed to read {file.name}: {e}")

    if len(all_frames) == 0:
        raise ValueError("❌ No valid CSV files were loaded. Check your data folder!")

    df_combined = pd.concat(all_frames, ignore_index=True)
    return df_combined


# ==========================================
# TASK 2: CORE AGGREGATION LOGIC
# ==========================================

def calculate_daily_totals(df):
    temp = df.set_index("timestamp")
    return temp.resample("D")["kwh"].sum().reset_index()

def calculate_weekly_aggregates(df):
    temp = df.set_index("timestamp")
    return temp.resample("W")["kwh"].sum().reset_index()

def building_wise_summary(df):
    summary = df.groupby("building")["kwh"].agg(
        ["mean", "min", "max", "sum"]
    )
    summary.rename(columns={"sum": "total"}, inplace=True)
    return summary


# ==========================================
# TASK 3: OBJECT ORIENTED MODELING
# ==========================================

class MeterReading:
    def __init__(self, timestamp, kwh):
        self.timestamp = timestamp
        self.kwh = kwh

class Building:
    def __init__(self, name):
        self.name = name
        self.meter_readings = []

    def add_reading(self, reading):
        self.meter_readings.append(reading)

    def calculate_total_consumption(self):
        return sum(r.kwh for r in self.meter_readings)

    def generate_report(self):
        return f"{self.name} Total Consumption: {self.calculate_total_consumption()} kWh"

class BuildingManager:
    def __init__(self):
        self.buildings = {}

    def add_reading(self, building_name, reading):
        if building_name not in self.buildings:
            self.buildings[building_name] = Building(building_name)
        self.buildings[building_name].add_reading(reading)

    def generate_all_reports(self):
        return [b.generate_report() for b in self.buildings.values()]


# ==========================================
# TASK 4: VISUALIZATION (MATPLOTLIB)
# ==========================================

def create_dashboard(df, daily, weekly, summary):
    plt.figure(figsize=(15, 8))

    plt.subplot(2, 2, 1)
    for b in df["building"].unique():
        sub = df[df["building"] == b]
        daily_b = sub.set_index("timestamp").resample("D")["kwh"].sum()
        plt.plot(daily_b.index, daily_b.values, label=b)

    plt.title("Daily Consumption Trend")
    plt.xlabel("Date")
    plt.ylabel("kWh")
    plt.legend()

    plt.subplot(2, 2, 2)
    plt.bar(summary.index, summary["mean"])
    plt.title("Average Weekly Usage by Building")
    plt.xlabel("Building")
    plt.ylabel("Avg kWh")

    plt.subplot(2, 1, 2)
    plt.scatter(df["timestamp"], df["kwh"], alpha=0.4)
    plt.title("Peak-Hour Consumption Scatter")
    plt.xlabel("Timestamp")
    plt.ylabel("kWh")

    plt.tight_layout()
    plt.savefig("dashboard.png")
    plt.close()

    print("Dashboard saved as dashboard.png")


# ==========================================
# TASK 5: EXPORT & EXECUTIVE SUMMARY
# ==========================================

def export_results(df, summary):
    df.to_csv("cleaned_energy_data.csv", index=False)
    summary.to_csv("building_summary.csv")

def create_summary_report(df, summary):
    total_consumption = df["kwh"].sum()
    highest_building = summary["total"].idxmax()
    max_consumption = summary.loc[highest_building, "total"]
    peak_time = df.loc[df["kwh"].idxmax(), "timestamp"]

    text = (
        f"Campus Total Consumption: {total_consumption} kWh\n"
        f"Highest Consuming Building: {highest_building} ({max_consumption} kWh)\n"
        f"Peak Load Time: {peak_time}\n"
        f"Daily & Weekly trends are shown in the dashboard image.\n"
    )

    with open("summary.txt", "w") as f:
        f.write(text)

    print("\nEXECUTIVE SUMMARY")
    print("---------------------")
    print(text)


# ==========================================
# MAIN PROGRAM (TO CONNECTS ALL TASKS)
# ==========================================

def main():
    print("Starting Energy Consumption Analysis...\n")

    df = ingest_data()                       
    daily = calculate_daily_totals(df)      
    weekly = calculate_weekly_aggregates(df)
    summary = building_wise_summary(df)

    create_dashboard(df, daily, weekly, summary)
    export_results(df, summary)                    
    create_summary_report(df, summary)

    print("✅ All tasks completed successfully!")

if __name__ == "__main__":
    main()
