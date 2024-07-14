import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

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

# Sidebar dropdown for selecting the entity type
filter_a = st.sidebar.selectbox("Filter [a]:", ['sku_name', 'brand_name', 'Category', 'Group'])

# Based on the selection from Filter [a], display a second dropdown menu showing all unique values for the selected entity
if filter_a:
    selected_entity = st.sidebar.selectbox(f"Select {filter_a}:", data[filter_a].unique())
    
    if selected_entity:
        # Analyze items bought with selected entity
        items_bought_with = analyze_items_bought_with(data, filter_a, selected_entity)
        
        # Convert dictionary to DataFrame for plotting
        df = pd.DataFrame.from_dict(items_bought_with, orient='index', columns=['Frequency'])
        
        # Sort items by frequency in descending order
        df = df.sort_values(by='Frequency', ascending=False)
        
        # Calculate total occurrences
        total_occurrences = df['Frequency'].sum()
        
        # Calculate percentages
        df['Percentage'] = (df['Frequency'] / total_occurrences) * 100
        
        # Print list of items along with percentages
        st.subheader(f"Items bought with '{selected_entity}' (Frequency and Percentage):")
        st.write(df)
        
        # Plot bar chart for frequency
        st.subheader(f"Bar Chart for items bought with '{selected_entity}' (Frequency):")
        plt.figure(figsize=(10, 6))
        plt.bar(df.index, df['Frequency'])
        plt.xlabel('Items')
        plt.ylabel('Frequency')
        plt.title(f'Items bought with {selected_entity} (Frequency)')
        plt.xticks(rotation=45, ha='right')
        st.pyplot(plt)
        
        # Plot bar chart for percentages
        st.subheader(f"Bar Chart for items bought with '{selected_entity}' (Percentage):")
        plt.figure(figsize=(10, 6))
        plt.bar(df.index, df['Percentage'])
        plt.xlabel('Items')
        plt.ylabel('Percentage')
        plt.title(f'Items bought with {selected_entity} (Percentage)')
        plt.xticks(rotation=45, ha='right')
        st.pyplot(plt)
