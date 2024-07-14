import streamlit as st
import pandas as pd

# Function to analyze items bought along with a specified item
def analyze_items_bought_with(data, item_type, selected_item):
    # Filter data for the selected item
    selected_item_data = data[data[item_type] == selected_item]
    
    # Get basket IDs for the selected item
    selected_item_basket_ids = selected_item_data['basket_id'].unique()
    
    # Initialize dictionary to store counts
    items_bought_with = {}
    
    # Iterate over basket IDs for the selected item
    for basket_id in selected_item_basket_ids:
        # Get data for the basket
        basket_data = data[data['basket_id'] == basket_id]
        
        # Exclude the selected item itself
        basket_data = basket_data[basket_data[item_type] != selected_item]
        
        # Count occurrences of other items bought along with the selected item
        for item in basket_data[item_type].unique():
            if item in items_bought_with:
                items_bought_with[item] += 1
            else:
                items_bought_with[item] = 1
    
    return items_bought_with

# Read the data
@st.cache
def load_data():
    data = pd.read_excel("DS_Round_1_Assignment.xlsx")
    return data

data_load_state = st.text('Loading data...')
data = load_data()
data_load_state.text('Data loaded successfully!')

# Sidebar title
st.sidebar.title('Market Basket Analysis')

# Sidebar dropdown for selecting the item
selected_item = st.sidebar.selectbox("Select an item:", data['sku_name'].unique())

# Analyze items bought with selected item
items_bought_with = analyze_items_bought_with(data, 'sku_name', selected_item)

# Calculate total occurrences
total_occurrences = sum(items_bought_with.values())

# Sort items bought with the selected item in descending order of frequency
sorted_items_bought_with = dict(sorted(items_bought_with.items(), key=lambda x: x[1], reverse=True))

# Print items bought with the selected item in descending order with percentages
st.subheader(f"Items bought with '{selected_item}' (in descending order of frequency and percentage):")
for item, count in sorted_items_bought_with.items():
    percentage = (count / total_occurrences) * 100
    st.write(f"- {item}: {count} times ({percentage:.2f}%)")
