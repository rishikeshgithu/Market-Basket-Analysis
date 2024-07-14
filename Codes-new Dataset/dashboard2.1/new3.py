import streamlit as st
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

# Function to process data and generate analysis
def process_data(file_path, filter_a, selected_entity, sort_by, num_items_to_show):
    # Load data
    data = load_data(file_path)

    # Count the number of transactions
    total_transactions = data['receipt_id'].nunique()

    # Count frequencies of antecedent
    antecedent_frequency = data[data[filter_a] == selected_entity].shape[0]

    # Count frequencies of consequent (all items)
    sku_name_counts, brand_name_counts, category_counts = count_frequencies(data)

    # Calculate support of antecedent
    antecedent_support = antecedent_frequency / total_transactions

    # Calculate support of (all items)
    sku_name_support = calculate_support(sku_name_counts, total_transactions)
    brand_name_support = calculate_support(brand_name_counts, total_transactions)
    category_support = calculate_support(category_counts, total_transactions)

    # Count items bought with selected antecedent
    items_bought_with_antecedent = count_items_bought_with_antecedent(data, filter_a, selected_entity)

    # Initialize empty lists to store results
    results = []

    # Calculate confidence, lift, and conviction for sku_name, brand_name, and category
    for entity in ['sku_name', 'brand_name', 'Category']:
        for item in items_bought_with_antecedent[entity]:
            support_ab = items_bought_with_antecedent[entity][item] / total_transactions
            support_a = antecedent_support
            support_b = 0

            # Determine support_b based on entity type
            if entity == 'sku_name':
                support_b = sku_name_support.get(item, 0)
            elif entity == 'brand_name':
                support_b = brand_name_support.get(item, 0)
            elif entity == 'Category':
                support_b = category_support.get(item, 0)

            confidence_ab = calculate_confidence(support_ab, support_a)
            lift_ab = calculate_lift(confidence_ab, support_b)
            conviction_ab = calculate_conviction(support_b, confidence_ab)

            # Append results
            results.append({
                'Entity': entity,
                'Item': item,
                'Support': support_ab,
                'Confidence': confidence_ab,
                'Lift': lift_ab,
                'Conviction': conviction_ab
            })

    # Convert results to DataFrame
    results_df = pd.DataFrame(results)

    # Sort by 'Lift' and select top items
    sorted_results = results_df.sort_values(by=sort_by, ascending=False).head(num_items_to_show)

    return sorted_results

def main():
    st.title('Transaction Analysis')

    # Sidebar for user input
    st.sidebar.header('Input Parameters')
    file_path = st.sidebar.file_uploader("Upload a file", type=['xlsx'])
    if file_path:
        filter_a = st.sidebar.selectbox('Select filter:', options=['sku_name', 'brand_name', 'Category'])
        selected_entity = st.sidebar.text_input('Enter selected entity:')
        sort_by = st.sidebar.selectbox('Select metric to sort by:', options=['Support', 'Confidence', 'Lift', 'Conviction'])
        num_items_to_show = st.sidebar.number_input('Number of items to show:', min_value=1, step=1, value=10)

        # Process data and generate analysis
        if st.sidebar.button('Generate Analysis'):
            if filter_a and selected_entity and sort_by and num_items_to_show:
                analysis_results = process_data(file_path, filter_a, selected_entity, sort_by, num_items_to_show)

                # Display results
                st.header('Analysis Results')
                st.write(analysis_results)

if __name__ == '__main__':
    main()
