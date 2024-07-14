import pandas as pd
import random
from mlxtend.frequent_patterns import apriori, association_rules

# Create a small synthetic dataset
data = pd.DataFrame({
    'Transaction ID': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    'Items Bought': [
        'Bread, Butter', 
        'Bread, Butter, Milk', 
        'Bread, Milk', 
        'Butter, Milk', 
        'Bread, Butter', 
        'Bread, Butter, Milk', 
        'Milk', 
        'Bread, Butter, Milk', 
        'Bread, Butter', 
        'Bread, Milk'
    ]
})

# Convert the dataset into a basket-item matrix
data['Items Bought'] = data['Items Bought'].apply(lambda x: x.split(', '))
basket_item_matrix = data.explode('Items Bought').pivot_table(index='Transaction ID', columns='Items Bought', aggfunc='size', fill_value=0)
basket_item_matrix = basket_item_matrix.applymap(lambda x: 1 if x > 0 else 0)

# Verify the basket-item matrix
print("Basket-Item Matrix:")
print(basket_item_matrix)

# Randomly select an item (SKU)
random_sku = random.choice(basket_item_matrix.columns)
print(f"\nRandomly selected SKU: {random_sku}")

# Filter the basket-item matrix for the selected SKU
filtered_basket_item_matrix = basket_item_matrix[basket_item_matrix[random_sku] == 1]

# Apply the Apriori algorithm to find frequent itemsets with a low minimum support threshold
min_support = 0.1  # Lower the support threshold
frequent_itemsets = apriori(filtered_basket_item_matrix, min_support=min_support, use_colnames=True)

# Verify the frequent itemsets
print("\nFrequent Itemsets:")
print(frequent_itemsets)

# Generate association rules with a low minimum confidence threshold
min_confidence = 0.1  # Lower the confidence threshold
rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=min_confidence)

# Verify the association rules
print("\nAssociation Rules:")
if rules.empty:
    print("No association rules found.")
else:
    print(rules)

# Add additional metrics to the rules dataframe
rules['leverage'] = rules['support'] - (rules['antecedent support'] * rules['consequent support'])
rules['conviction'] = (1 - rules['consequent support']) / (1 - rules['confidence'])

# Display the rules with the additional metrics
print("\nAssociation Rules with Additional Metrics:")
print(rules)
