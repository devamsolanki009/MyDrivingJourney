import matplotlib.pyplot as plt
import pandas as pd

# 1. Load the dataset
file_name = "ROA37.20261107121327.csv"
df = pd.read_csv(file_name)

# 2. Data Preparation
# Convert TLIST(M1) integer (e.g., 202109) into a proper datetime object for time-series plotting
df["Month_Date"] = pd.to_datetime(df["TLIST(M1)"].astype(str), format="%Y%m")

# Filter for Co. Cork and National Average (Ireland)
cork_data = df[df["County"] == "Co. Cork"].sort_values("Month_Date")
ireland_data = df[df["County"] == "Ireland"].sort_values("Month_Date")

# 3. Print Summary Statistics
print("=== CO. CORK WAITING TIME STATS (WEEKS) ===")
print(cork_data["VALUE"].describe())

print("\n=== NATIONAL AVERAGE STATS (WEEKS) ===")
print(ireland_data["VALUE"].describe())

# 4. Generate Visualization
plt.figure(figsize=(12, 6))

plt.plot(
    cork_data["Month_Date"],
    cork_data["VALUE"],
    label="Co. Cork",
    color="#1f77b4",
    linewidth=2.5,
    marker="o",
    markersize=4,
)
plt.plot(
    ireland_data["Month_Date"],
    ireland_data["VALUE"],
    label="National Average (Ireland)",
    color="#ff7f0e",
    linestyle="--",
    linewidth=2,
)

plt.title(
    "Estimated Time to Car Test Invite: Co. Cork vs. National Average",
    fontsize=14,
    fontweight="bold",
    pad=15,
)
plt.xlabel("Timeline", fontsize=11, labelpad=10)
plt.ylabel("Estimated Wait Time (Weeks)", fontsize=11, labelpad=10)

plt.grid(True, linestyle=":", alpha=0.6)
plt.legend(fontsize=11)
plt.tight_layout()

# Save and show plot
plt.savefig("cork_vs_national_test_wait_times.png", dpi=300)
print(
    "\n[SUCCESS] Plot saved successfully as 'cork_vs_national_test_wait_times.png'."
)
plt.show()