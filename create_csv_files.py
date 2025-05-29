import pandas as pd

# Create trips.csv
trips_df = pd.DataFrame(columns=["Trip_Name"])
trips_df.to_csv("trips.csv", index=False)

# Create families.csv
families_df = pd.DataFrame(columns=["Trip_Name", "Family", "Gmail", "Fixed_Amount"])
families_df.to_csv("families.csv", index=False)

# Create expenses.csv
expenses_df = pd.DataFrame(columns=["Trip_Name", "Date", "Spent_By", "Amount", "Reason", "Remarks"])
expenses_df.to_csv("expenses.csv", index=False)

print("CSV files created successfully!") 