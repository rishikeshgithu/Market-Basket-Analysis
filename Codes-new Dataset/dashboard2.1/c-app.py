import pandas as pd

# Function to load data
def load_data(file_path):
    data = pd.read_excel(file_path)
    return data

# Function to count frequencies of items in specified columns
def count_frequencies(data):
    sku_name_counts = data['sku_name'].value_counts().to_dict()
    brand_name_counts = data['brand_name'].value_counts().to_dict()
    category_counts = data['Category'].value_counts().to_dict()

    return sku_name_counts, brand_name_counts, category_counts

# Load data
data = load_data("Sample_Transaction_Data.xlsx")

# Count frequencies of all items
sku_name_counts, brand_name_counts, category_counts = count_frequencies(data)

# Calculate total number of transactions
total_transactions = data['receipt_id'].nunique()

# Calculate support for sku_names
sku_name_support = {sku_name: count / total_transactions if count / total_transactions >= 0 else 0 for sku_name, count in sku_name_counts.items()}

# Calculate support for brand_names
brand_name_support = {brand_name: count / total_transactions if count / total_transactions >= 0 else 0 for brand_name, count in brand_name_counts.items()}

# Calculate support for categories
category_support = {category: count / total_transactions if count / total_transactions >= 0 else 0 for category, count in category_counts.items()}

# Print frequencies and supports
print("Frequency and Support of sku_names:")
for sku_name, count in sku_name_counts.items():
    print(f"{sku_name}: Frequency = {count}, Support = {sku_name_support[sku_name]:.20f}")

print("\nFrequency and Support of brand_names:")
for brand_name, count in brand_name_counts.items():
    print(f"{brand_name}: Frequency = {count}, Support = {brand_name_support[brand_name]:.20f}")

print("\nFrequency and Support of categories:")
for category, count in category_counts.items():
    print(f"{category}: Frequency = {count}, Support = {category_support[category]:.20f}")

# Print total number of transactions
print(f"\nTotal number of transactions: {total_transactions}")
