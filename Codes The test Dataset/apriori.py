import pandas as pd
import random
from mlxtend.frequent_patterns import apriori, association_rules

# Load the Excel file into a DataFrame
data = pd.read_excel("DS_Round_1_Assignment.xlsx")

# Create a basket-item matrix where each row represents a basket, and each column represents an item (SKU)
basket_item_matrix = data.pivot_table(index='basket_id', columns='sku_name', aggfunc='size', fill_value=0)

# Convert quantities to binary values (1 if the item is present, 0 otherwise)
basket_item_matrix = basket_item_matrix.applymap(lambda x: 1 if x > 0 else 0)

# Verify the basket-item matrix
print("Basket-Item Matrix:")
print(basket_item_matrix.head())

# Randomly select an SKU
random_sku = random.choice(data['sku_name'].unique())
print(f"Randomly selected SKU: {random_sku}")

# Filter the basket-item matrix for the selected SKU
filtered_basket_item_matrix = basket_item_matrix[basket_item_matrix[random_sku] == 1]

# Apply the Apriori algorithm to find frequent itemsets with a low minimum support threshold
min_support = 0.001  # Lower the support threshold
frequent_itemsets = apriori(filtered_basket_item_matrix, min_support=min_support, use_colnames=True)

# Verify the frequent itemsets
print("Frequent Itemsets:")
print(frequent_itemsets)

# Generate association rules with a low minimum confidence threshold
min_confidence = 0.01  # Lower the confidence threshold
rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=min_confidence)

# Verify the association rules
print("Association Rules:")
if rules.empty:
    print("No association rules found.")
else:
    print(rules)

# Add additional metrics to the rules dataframe
rules['leverage'] = rules['support'] - (rules['antecedent support'] * rules['consequent support'])
rules['conviction'] = (1 - rules['consequent support']) / (1 - rules['confidence'])

# Display the rules with the additional metrics
print("Association Rules with Additional Metrics:")
print(rules)

# Sort the rules by Lift in descending order and print the top rules
sorted_rules_by_lift = rules.sort_values(by='lift', ascending=False)
print("Top Association Rules sorted by Lift:")
print(sorted_rules_by_lift.head())
