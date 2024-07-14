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

# Function to count items bought with antecedent
def count_items_bought_with_antecedent(data, item_type, selected_entity):
    items_bought_with = {
        'sku_name': {},
        'brand_name': {},
        'Category': {}
    }

    # Filter transactions where antecedent (selected_entity) appears
    selected_item_data = data[data[item_type] == selected_entity]
    selected_item_receipt_ids = selected_item_data['receipt_id'].unique()

    # Iterate through each transaction where antecedent appears
    for receipt_id in selected_item_receipt_ids:
        receipt_data = data[data['receipt_id'] == receipt_id]
        receipt_data = receipt_data[receipt_data[item_type] != selected_entity]  # Exclude the antecedent itself
        for entity in items_bought_with.keys():
            entities = receipt_data[entity].unique()
            for item in entities:
                if item in items_bought_with[entity]:
                    items_bought_with[entity][item] += 1
                else:
                    items_bought_with[entity][item] = 1

    return items_bought_with

# Function to calculate support
def calculate_support(count_dict, total_transactions):
    return {item: count / total_transactions if count / total_transactions >= 0 else 0 for item, count in count_dict.items()}

# Function to calculate confidence
def calculate_confidence(support_ab, support_a):
    return support_ab / support_a if support_a > 0 else 0

# Function to calculate lift
def calculate_lift(confidence_ab, support_b):
    return confidence_ab / support_b if support_b > 0 else 0

# Function to calculate conviction
def calculate_conviction(support_b, confidence_ab):
    return (1 - support_b) / (1 - confidence_ab) if confidence_ab < 1 else float('inf')

# Load data
data = load_data("Sample_Transaction_Data.xlsx")

# Count the number of transactions
total_transactions = data['receipt_id'].nunique()

# Select antecedent
antecedent_type = 'sku_name'
selected_antecedent = 'Prod_1'

# Count frequencies of antecedent
antecedent_frequency = data[data[antecedent_type] == selected_antecedent].shape[0]

# Count frequencies of consequent (all items)
sku_name_counts, brand_name_counts, category_counts = count_frequencies(data)

# Calculate support of antecedent
antecedent_support = antecedent_frequency / total_transactions

# Calculate support of (all items)
sku_name_support = calculate_support(sku_name_counts, total_transactions)
brand_name_support = calculate_support(brand_name_counts, total_transactions)
category_support = calculate_support(category_counts, total_transactions)

# Count items bought with selected antecedent
items_bought_with_antecedent = count_items_bought_with_antecedent(data, antecedent_type, selected_antecedent)

# Calculate support for items bought with antecedent
sku_name_bought_with_support = calculate_support(items_bought_with_antecedent['sku_name'], total_transactions)
brand_name_bought_with_support = calculate_support(items_bought_with_antecedent['brand_name'], total_transactions)
category_bought_with_support = calculate_support(items_bought_with_antecedent['Category'], total_transactions)

# Calculate support for transactions where antecedent and consequent are bought together
antecedent_consequent_support = {
    'sku_name': {},
    'brand_name': {},
    'Category': {}
}

# Filter transactions where antecedent appears
selected_item_data = data[data[antecedent_type] == selected_antecedent]
selected_item_receipt_ids = selected_item_data['receipt_id'].unique()

# Iterate through each transaction where antecedent appears
for receipt_id in selected_item_receipt_ids:
    receipt_data = data[data['receipt_id'] == receipt_id]
    consequent_data = receipt_data[receipt_data[antecedent_type] != selected_antecedent]  # Exclude the antecedent itself
    for entity in antecedent_consequent_support.keys():
        entities = consequent_data[entity].unique()
        for item in entities:
            if item in antecedent_consequent_support[entity]:
                antecedent_consequent_support[entity][item] += 1
            else:
                antecedent_consequent_support[entity][item] = 1

# Calculate support for antecedent and consequent together
sku_name_antecedent_consequent_support = calculate_support(antecedent_consequent_support['sku_name'], total_transactions)
brand_name_antecedent_consequent_support = calculate_support(antecedent_consequent_support['brand_name'], total_transactions)
category_antecedent_consequent_support = calculate_support(antecedent_consequent_support['Category'], total_transactions)

# Create dataframes
sku_name_df = pd.DataFrame.from_dict(sku_name_support, orient='index', columns=['Support'])
brand_name_df = pd.DataFrame.from_dict(brand_name_support, orient='index', columns=['Support'])
category_df = pd.DataFrame.from_dict(category_support, orient='index', columns=['Support'])

# Adding Frequency to dataframes
sku_name_df['Frequency'] = sku_name_counts
brand_name_df['Frequency'] = brand_name_counts
category_df['Frequency'] = category_counts

# Adding Confidence, Lift, and Conviction
for df, entity_support, antecedent_support in [
    (sku_name_df, sku_name_antecedent_consequent_support, sku_name_support),
    (brand_name_df, brand_name_antecedent_consequent_support, brand_name_support),
    (category_df, category_antecedent_consequent_support, category_support),
]:
    df['Confidence'] = df.apply(lambda row: calculate_confidence(entity_support.get(row.name, 0), antecedent_support), axis=1)
    df['Lift'] = df.apply(lambda row: calculate_lift(row['Confidence'], entity_support.get(row.name, 0)), axis=1)
    df['Conviction'] = df.apply(lambda row: calculate_conviction(entity_support.get(row.name, 0), row['Confidence']), axis=1)

# Display the dataframes
print("sku_name DataFrame:")
print(sku_name_df)

print("\nbrand_name DataFrame:")
print(brand_name_df)

print("\nCategory DataFrame:")
print(category_df)
