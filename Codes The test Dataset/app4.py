import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

# Function to analyze items bought along with a specified item
def analyze_items_bought_with(data, item_type, selected_item):
    # Filter data for the selected item
    selected_item_data = data[data[item_type] == selected_item]
    
    # Get basket IDs for the selected item
    selected_item_basket_ids = selected_item_data['basket_id'].unique()
    
    # Initialize dictionaries to store counts for different entities
    items_bought_with = {}
    brands_bought_with = {}
    categories_bought_with = {}
    groups_bought_with = {}
    skus_bought_with = {}
    
    # Iterate over basket IDs for the selected item
    for basket_id in selected_item_basket_ids:
        # Get data for the basket
        basket_data = data[data['basket_id'] == basket_id]
        
        # Exclude the selected item itself
        basket_data = basket_data[basket_data[item_type] != selected_item]
        
        # Extract other entities from the basket data
        skus = basket_data['sku_name'].unique()
        brands = basket_data['brand_name'].unique()
        categories = basket_data['Category'].unique()
        groups = basket_data['Group'].unique()
        
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
    selected_entity = st.sidebar.selectbox(f"Filter [b]: Select {filter_a}:", data[filter_a].unique())
    
    if selected_entity:
        # Analyze items bought with selected entity
        items_bought_with = analyze_items_bought_with(data, filter_a, selected_entity)
        
        # Convert dictionaries to DataFrames for plotting
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
        
        # Print list of items along with percentages
        st.subheader(f"Items bought with '{selected_entity}' (Frequency and Percentage):")
        st.write("SKUs:")
        st.write(df_skus)
        st.write("Brands:")
        st.write(df_brands)
        st.write("Categories:")
        st.write(df_categories)
        st.write("Groups:")
        st.write(df_groups)
        
        # Plot bar charts for frequency of SKUs, brands, categories, and groups
        st.subheader(f"Bar Chart for items bought with '{selected_entity}' (Frequency):")
        with st.expander("Click to expand and view"):
            fig, axs = plt.subplots(4, 1, figsize=(10, 40))
            
            axs[0].bar(df_skus.index, df_skus['Frequency'], color='skyblue')
            axs[0].set_xlabel('SKUs')
            axs[0].set_ylabel('Frequency')
            axs[0].set_title(f'SKUs bought with {selected_entity} (Frequency)')
            axs[0].tick_params(axis='x', rotation=90)
            
            axs[1].bar(df_brands.index, df_brands['Frequency'], color='lightgreen')
            axs[1].set_xlabel('Brands')
            axs[1].set_ylabel('Frequency')
            axs[1].set_title(f'Brands bought with {selected_entity} (Frequency)')
            axs[1].tick_params(axis='x', rotation=90)
            
            axs[2].bar(df_categories.index, df_categories['Frequency'], color='lightcoral')
            axs[2].set_xlabel('Categories')
            axs[2].set_ylabel('Frequency')
            axs[2].set_title(f'Categories bought with {selected_entity} (Frequency)')
            axs[2].tick_params(axis='x', rotation=90)
            
            axs[3].bar(df_groups.index, df_groups['Frequency'], color='lightskyblue')
            axs[3].set_xlabel('Groups')
            axs[3].set_ylabel('Frequency')
            axs[3].set_title(f'Groups bought with {selected_entity} (Frequency)')
            axs[3].tick_params(axis='x', rotation=90)
            
            plt.tight_layout()
            st.pyplot(fig)
        
        # Plot bar charts for percentages of SKUs, brands, categories, and groups
        st.subheader(f"Bar Chart for items bought with '{selected_entity}' (Percentage):")
        with st.expander("Click to expand and view"):
            fig, axs = plt.subplots(4, 1, figsize=(10, 40))
            
            axs[0].bar(df_skus.index, df_skus['Percentage'], color='skyblue')
            axs[0].set_xlabel('SKUs')
            axs[0].set_ylabel('Percentage')
            axs[0].set_title(f'SKUs bought with {selected_entity} (Percentage)')
            axs[0].tick_params(axis='x', rotation=90)
            
            axs[1].bar(df_brands.index, df_brands['Percentage'], color='lightgreen')
            axs[1].set_xlabel('Brands')
            axs[1].set_ylabel('Percentage')
            axs[1].set_title(f'Brands bought with {selected_entity} (Percentage)')
            axs[1].tick_params(axis='x', rotation=90)
            
            axs[2].bar(df_categories.index, df_categories['Percentage'], color='lightcoral')
            axs[2].set_xlabel('Categories')
            axs[2].set_ylabel('Percentage')
            axs[2].set_title(f'Categories bought with {selected_entity} (Percentage)')
            axs[2].tick_params(axis='x', rotation=90)
            
            axs[3].bar(df_groups.index, df_groups['Percentage'], color='lightskyblue')
            axs[3].set_xlabel('Groups')
            axs[3].set_ylabel('Percentage')
            axs[3].set_title(f'Groups bought with {selected_entity} (Percentage)')
            axs[3].tick_params(axis='x', rotation=90)
            
            plt.tight_layout()
            st.pyplot(fig)
        
        # Plot pie charts for percentages of SKUs, brands, categories, and groups
        st.subheader(f"Pie Chart for items bought with '{selected_entity}' (Percentage):")
        with st.expander("Click to expand and view"):
            fig, axs = plt.subplots(2, 2, figsize=(20, 20))
            
            # Pie chart for SKUs
            colors = plt.cm.tab20c.colors[:len(df_skus)]
            axs[0, 0].pie(df_skus['Percentage'], labels=df_skus.index, autopct='%1.1f%%', colors=colors)
            axs[0, 0].set_title(f'SKUs bought with {selected_entity}')
            
            # Pie chart for Brands
            colors = plt.cm.tab20b.colors[:len(df_brands)]
            axs[0, 1].pie(df_brands['Percentage'], labels=df_brands.index, autopct='%1.1f%%', colors=colors)
            axs[0, 1].set_title(f'Brands bought with {selected_entity}')
            
            # Pie chart for Categories
            colors = plt.cm.tab20.colors[:len(df_categories)]
            axs[1, 0].pie(df_categories['Percentage'], labels=df_categories.index, autopct='%1.1f%%', colors=colors)
            axs[1, 0].set_title(f'Categories bought with {selected_entity}')
            
            # Pie chart for Groups
            colors = plt.cm.tab10.colors[:len(df_groups)]
            axs[1, 1].pie(df_groups['Percentage'], labels=df_groups.index, autopct='%1.1f%%', colors=colors)
            axs[1, 1].set_title(f'Groups bought with {selected_entity}')
            
            plt.tight_layout()
            st.pyplot(fig)

            # Legend for color and entity
            st.write("Legend:")
            st.write("SKUs:")
            for sku, color in zip(df_skus.index, colors):
                st.write(f"- {sku}: ", color)
            st.write("Brands:")
            for brand, color in zip(df_brands.index, colors):
                st.write(f"- {brand}: ", color)
            st.write("Categories:")
            for category, color in zip(df_categories.index, colors):
                st.write(f"- {category}: ", color)
            st.write("Groups:")
            for group, color in zip(df_groups.index, colors):
                st.write(f"- {group}: ", color)