import streamlit as st
import pandas as pd

# Function to calculate antecedent support
def calculate_antecedent_support(data, item_type, selected_item):
    # Count the number of transactions containing the selected item
    transactions_with_item = data[data[item_type] == selected_item]['receipt_id'].nunique()
    
    # Total number of transactions
    total_transactions = data['receipt_id'].nunique()
    
    # Calculate antecedent support
    antecedent_support = transactions_with_item / total_transactions
    
    return antecedent_support

# Function to calculate consequent support for each product
def calculate_consequent_support(data):
    # Total number of transactions
    total_transactions = data['receipt_id'].nunique()
    
    # Calculate support for each product
    support_dict = {}
    for product in data['sku_name'].unique():
        transactions_with_product = data[data['sku_name'] == product]['receipt_id'].nunique()
        support = transactions_with_product / total_transactions
        support_dict[product] = support
    
    return support_dict

# Function to analyze items bought along with a specified item
def analyze_items_bought_with(data, item_type, selected_item):
    # Filter data for the selected item
    selected_item_data = data[data[item_type] == selected_item]
    
    # Get receipt IDs for the selected item
    selected_item_receipt_ids = selected_item_data['receipt_id'].unique()
    
    # Initialize dictionaries to store counts for different entities
    items_bought_with = {}
    brands_bought_with = {}
    categories_bought_with = {}
    groups_bought_with = {}
    skus_bought_with = {}
    
    # Iterate over receipt IDs for the selected item
    for receipt_id in selected_item_receipt_ids:
        # Get data for the receipt
        receipt_data = data[data['receipt_id'] == receipt_id]
        
        # Exclude the selected item itself
        receipt_data = receipt_data[receipt_data[item_type] != selected_item]
        
        # Extract other entities from the receipt data
        skus = receipt_data['sku_name'].unique()
        brands = receipt_data['brand_name'].unique()
        categories = receipt_data['Category'].unique()
        groups = receipt_data['Group'].unique()
        
        # Count occurrences of other entities bought along with the selected item
        for sku in skus:
            if sku in skus_bought_with:
                skus_bought_with[sku] += 1
            else:
                skus_bought_with[sku] = 1
        
        for brand in brands:
            if brand in brands_bought_with:
                brands_bought_with[brand] += 1
            else:
                brands_bought_with[brand] = 1
        
        for category in categories:
            if category in categories_bought_with:
                categories_bought_with[category] += 1
            else:
                categories_bought_with[category] = 1
        
        for group in groups:
            if group in groups_bought_with:
                groups_bought_with[group] += 1
            else:
                groups_bought_with[group] = 1
    
    # Combine the counts for different entities into a single dictionary
    items_bought_with['skus'] = skus_bought_with
    items_bought_with['brands'] = brands_bought_with
    items_bought_with['categories'] = categories_bought_with
    items_bought_with['groups'] = groups_bought_with
    
    return items_bought_with

# Read the data
@st.cache
def load_data():
    data = pd.read_excel("Sample_Transaction_Data.xlsx")
    return data

data_load_state = st.text('Loading data...')
data = load_data()
data_load_state.text('Data loaded successfully!')

# Sidebar title
st.sidebar.title('Market Basket Analysis')

# Sidebar dropdown for selecting the entity type
filter_a = st.sidebar.selectbox("Filter [a]:", ['sku_name', 'brand_name', 'Category', 'Group'])

# Based on the selection from Filter [a], display a second dropdown menu showing all unique values for the selected entity
if filter_a:
    selected_entity = st.sidebar.selectbox(f"Filter [b]: Select {filter_a}:", data[filter_a].unique())
    
    if selected_entity:
        # Calculate antecedent support for the selected item
        antecedent_support = calculate_antecedent_support(data, filter_a, selected_entity)
        
        # Display antecedent support
        st.subheader(f"Antecedent Support of '{selected_entity}':")
        st.write(f"The antecedent support of '{selected_entity}' is: {antecedent_support:.2%}")
        
        # Calculate consequent support for each product
        consequent_support_dict = calculate_consequent_support(data)
        
        # Display consequent support for each product
        st.subheader(f"Consequent Support for Each Product:")
        st.write(consequent_support_dict)
        
        # Analyze items bought with selected entity
        items_bought_with = analyze_items_bought_with(data, filter_a, selected_entity)
        
        # Convert dictionaries to DataFrames for display
        df_skus = pd.DataFrame.from_dict(items_bought_with['skus'], orient='index', columns=['Frequency'])
        df_brands = pd.DataFrame.from_dict(items_bought_with['brands'], orient='index', columns=['Frequency'])
        df_categories = pd.DataFrame.from_dict(items_bought_with['categories'], orient='index', columns=['Frequency'])
        df_groups = pd.DataFrame.from_dict(items_bought_with['groups'], orient='index', columns=['Frequency'])
        
        # Sort DataFrames by frequency in descending order
        df_skus = df_skus.sort_values(by='Frequency', ascending=False)
        df_brands = df_brands.sort_values(by='Frequency', ascending=False)
        df_categories = df_categories.sort_values(by='Frequency', ascending=False)
        df_groups = df_groups.sort_values(by='Frequency', ascending=False)
        
        # Calculate total occurrences for each entity
        total_occurrences_skus = df_skus['Frequency'].sum()
        total_occurrences_brands = df_brands['Frequency'].sum()
        total_occurrences_categories = df_categories['Frequency'].sum()
        total_occurrences_groups = df_groups['Frequency'].sum()
        
        # Calculate percentages for each entity
        df_skus['Percentage'] = (df_skus['Frequency'] / total_occurrences_skus) * 100
        df_brands['Percentage'] = (df_brands['Frequency'] / total_occurrences_brands) * 100
        df_categories['Percentage'] = (df_categories['Frequency'] / total_occurrences_categories) * 100
        df_groups['Percentage'] = (df_groups['Frequency'] / total_occurrences_groups) * 100
        
        # Display tables with the new consequent support column
        st.subheader(f"Items bought with '{selected_entity}' (Frequency and Percentage):")
        st.write("SKUs:")
        st.write(df_skus)
        st.write("Brands:")
        st.write(df_brands)
        st.write("Categories:")
        st.write(df_categories)
        st.write("Groups:")
        st.write(df_groups)



