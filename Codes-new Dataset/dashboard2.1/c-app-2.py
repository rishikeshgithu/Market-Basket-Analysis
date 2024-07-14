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

# Print frequencies and supports
print("Frequency and Support of sku_names:")
for sku_name, count in sku_name_counts.items():
    print(f"{sku_name}: Frequency = {count}, Support = {sku_name_support.get(sku_name, 0):.20f}")

print("\nFrequency and Support of brand_names:")
for brand_name, count in brand_name_counts.items():
    print(f"{brand_name}: Frequency = {count}, Support = {brand_name_support.get(brand_name, 0):.20f}")

print("\nFrequency and Support of categories:")
for category, count in category_counts.items():
    print(f"{category}: Frequency = {count}, Support = {category_support.get(category, 0):.20f}")

# Print support for items bought with antecedent
print(f"\nSupport of {antecedent_type} bought with '{selected_antecedent}':")
for sku_name, support in sku_name_bought_with_support.items():
    print(f"{sku_name}: {support:.20f}")

print(f"\nSupport of brand_name bought with '{selected_antecedent}':")
for brand_name, support in brand_name_bought_with_support.items():
    print(f"{brand_name}: {support:.20f}")

print(f"\nSupport of Category bought with '{selected_antecedent}':")
for category, support in category_bought_with_support.items():
    print(f"{category}: {support:.20f}")

# Print support for antecedent and consequent together
print(f"\nSupport of {antecedent_type} and consequent bought together:")
for sku_name, support in sku_name_antecedent_consequent_support.items():
    print(f"{sku_name}: {support:.20f}")

print(f"\nSupport of brand_name and '{antecedent_type}' bought together:")
for brand_name, support in brand_name_antecedent_consequent_support.items():
    print(f"{brand_name}: {support:.20f}")

print(f"\nSupport of Category and '{antecedent_type}' bought together:")
for category, support in category_antecedent_consequent_support.items():
    print(f"{category}: {support:.20f}")

# Print total number of transactions
print(f"\nTotal number of transactions: {total_transactions}")


def calculate_confidence(support_ab, support_a):
    return support_ab / support_a if support_a > 0 else 0

# Lift of Prod_1 -> B
def calculate_lift(confidence_ab, support_b):
    return confidence_ab / support_b if support_b > 0 else 0

# Conviction of Prod_1 -> B
def calculate_conviction(support_b, confidence_ab):
    return (1 - support_b) / (1 - confidence_ab) if confidence_ab < 1 else float('inf')

# Calculate confidence, lift, and conviction for sku_name, brand_name, and category
confidence_lift_conviction = {}
for entity in ['sku_name', 'brand_name', 'Category']:
    confidence_lift_conviction[entity] = {}

    # Calculate confidence, lift, and conviction for each item in the entity
    for item in items_bought_with_antecedent[entity]:
        support_ab = items_bought_with_antecedent[entity][item] / total_transactions
        support_a = antecedent_support
        support_b = 0
        if entity == 'sku_name':
            support_b = sku_name_support.get(item, 0)
        elif entity == 'brand_name':
            support_b = brand_name_support.get(item, 0)
        elif entity == 'Category':
            support_b = category_support.get(item, 0)

        confidence_ab = calculate_confidence(support_ab, support_a)
        lift_ab = calculate_lift(confidence_ab, support_b)
        conviction_ab = calculate_conviction(support_b, confidence_ab)

        confidence_lift_conviction[entity][item] = {
            'Confidence': confidence_ab,
            'Lift': lift_ab,
            'Conviction': conviction_ab
        }

# Print confidence, lift, and conviction for sku_name, brand_name, and category
for entity in ['sku_name', 'brand_name', 'Category']:
    print(f"\nConfidence, Lift, and Conviction of Prod_1 -> {entity} bought together:")
    for item, metrics in confidence_lift_conviction[entity].items():
        print(f"{item}:")
        print(f"  Confidence: {metrics['Confidence']:.20f}")
        print(f"  Lift: {metrics['Lift']:.20f}")
        print(f"  Conviction: {metrics['Conviction']:.20f}")