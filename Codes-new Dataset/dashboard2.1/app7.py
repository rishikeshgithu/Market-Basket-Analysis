import streamlit as st  # Streamlit for web app
import pandas as pd  # Pandas for data manipulation
import matplotlib.pyplot as plt  # Matplotlib for plotting
import plotly.graph_objects as go  # Plotly for interactive plots

# Set page layout to wide
st.set_page_config(layout="wide")  # Set layout to wide for better visualization

# Function to calculate antecedent support
def calculate_antecedent_support(data, item_type, selected_item):
    transactions_with_item = data[data[item_type] == selected_item]['receipt_id'].nunique()  # Count unique transactions with the selected item
    total_transactions = data['receipt_id'].nunique()  # Count total unique transactions
    antecedent_support = transactions_with_item / total_transactions  # Calculate antecedent support
    return antecedent_support  # Return antecedent support

# Function to calculate consequent support for each product
def calculate_consequent_support(data):
    total_transactions = data['receipt_id'].nunique()  # Count total unique transactions
    support_dict = {}  # Initialize support dictionary
    for product in data['sku_name'].unique():  # Loop through unique products
        transactions_with_product = data[data['sku_name'] == product]['receipt_id'].nunique()  # Count unique transactions with the product
        support = transactions_with_product / total_transactions  # Calculate support
        support_dict[product] = support  # Store support in dictionary
    return support_dict  # Return support dictionary

# Function to analyze items bought along with a specified item
def analyze_items_bought_with(data, item_type, selected_item):
    selected_item_data = data[data[item_type] == selected_item]  # Filter data for selected item
    selected_item_receipt_ids = selected_item_data['receipt_id'].unique()  # Get unique receipt IDs with the selected item
    items_bought_with = {
        'sku_name': {},  # Initialize dictionary for SKU names
        'brand_name': {},  # Initialize dictionary for brand names
        'Category': {}  # Initialize dictionary for categories
    }
    for receipt_id in selected_item_receipt_ids:  # Loop through selected item receipt IDs
        receipt_data = data[data['receipt_id'] == receipt_id]  # Get data for the receipt
        receipt_data = receipt_data[receipt_data[item_type] != selected_item]  # Exclude the selected item
        for entity in items_bought_with.keys():  # Loop through entity types
            entities = receipt_data[entity].unique()  # Get unique entities
            for item in entities:  # Loop through entities
                if item in items_bought_with[entity]:  # Check if item already in dictionary
                    items_bought_with[entity][item] += 1  # Increment count
                else:
                    items_bought_with[entity][item] = 1  # Initialize count
    return items_bought_with  # Return items bought with dictionary

# Read the data
@st.cache_data  # Cache the data loading function to improve performance
def load_data():
    data = pd.read_excel("Sample_Transaction_Data.xlsx")  # Load data from Excel file
    return data  # Return loaded data

# Display a loading spinner while loading data
with st.spinner('Loading data...'):  # Show spinner while loading data
    data = load_data()  # Load data

# Page title
st.title('Market Basket Analysis with Apriori Algorithm')  # Set page title

# Horizontal layout for filters
col1, col2, col3, col4 = st.columns(4)  # Create four columns for filters

with col1:  # Column 1
    # Dropdown for selecting the entity type
    filter_a = st.selectbox("Filter [a]:", ['sku_name', 'brand_name', 'Category'])  # Dropdown for entity type

with col2:  # Column 2
    if filter_a:  # If entity type is selected
        # Based on the selection from Filter [a], display a second dropdown menu showing all unique values for the selected entity
        selected_entity = st.selectbox(f"Filter [b]: Select {filter_a}:", data[filter_a].unique())  # Dropdown for entity values

with col3:  # Column 3
    # Dropdown for selecting the sorting criterion
    sort_by = st.selectbox("Sort by:", ['Support', 'Confidence', 'Lift', 'Conviction'])  # Dropdown for sorting criterion

with col4:  # Column 4
    # Slider for selecting the number of items to show
    num_items_to_show = st.slider('Number of Items to Show:', min_value=1, max_value=20, value=10)  # Slider for number of items

if filter_a and selected_entity and sort_by:  # If all filters are selected
    antecedent_support = calculate_antecedent_support(data, filter_a, selected_entity)  # Calculate antecedent support
    consequent_support_dict = calculate_consequent_support(data)  # Calculate consequent support
    items_bought_with = analyze_items_bought_with(data, filter_a, selected_entity)  # Analyze items bought with selected item
    dataframes = {}  # Initialize dictionary for dataframes

    total_transactions = data['receipt_id'].nunique()  # Calculate total transactions

    for entity, counts in items_bought_with.items():  # Loop through items bought with
        df = pd.DataFrame.from_dict(counts, orient='index', columns=['Frequency'])  # Create dataframe from counts
        df['Support'] = (df['Frequency'] / total_transactions) * 100  # Calculate support
        df['Confidence'] = df['Frequency'] / (antecedent_support * total_transactions)  # Calculate confidence
        df['Lift'] = df.apply(lambda row: row['Frequency'] / (antecedent_support * consequent_support_dict.get(row.name, 0.0001) * total_transactions), axis=1)  # Calculate lift
        df['Conviction'] = df.apply(lambda row: max((1 - consequent_support_dict.get(row.name, 0.0001)) / (1 - row['Confidence']), 0), axis=1)  # Calculate conviction
        df = df.sort_values(by=sort_by, ascending=False).head(num_items_to_show)  # Sort dataframe by selected criterion
        dataframes[entity] = df  # Store dataframe in dictionary

    st.subheader(f"Antecedent Support of '{selected_entity}':")  # Subheader for antecedent support
    st.write(f"The antecedent support of '{selected_entity}' is: {antecedent_support:.2%}")  # Display antecedent support

    # Display gauge chart for antecedent support
    fig = go.Figure(go.Indicator(
        mode="gauge+number",  # Gauge mode
        value=antecedent_support * 100,  # Antecedent support value
        title={'text': "Percentage of transactions this entity bought alongside others"},  # Title
        gauge={
            'axis': {'range': [0, 100]},  # Gauge axis range
            'bar': {'color': "green"},  # Bar color
        }
    ))
    st.plotly_chart(fig)  # Display gauge chart

    # Display bar charts and data tables in a 2x2 grid
    chart_cols = st.columns(2)  # Create two columns for charts
    table_cols = st.columns(2)  # Create two columns for tables

    chart_count = 0  # Initialize chart counter
    table_count = 0  # Initialize table counter
    for entity, df in dataframes.items():  # Loop through dataframes
        with chart_cols[chart_count % 2]:  # Alternate between chart columns
            st.subheader(f"{entity} Distribution (sorted by {sort_by}):")  # Subheader for distribution
            sorted_df = df.sort_values(by=sort_by, ascending=True)  # Sort dataframe by selected criterion
            plt.figure(figsize=(10, 6))  # Create figure
            plt.barh(sorted_df.index.astype(str), sorted_df[sort_by])  # Create horizontal bar chart
            plt.xlabel(sort_by)  # Set x-axis label
            plt.ylabel(selected_entity)  # Set y-axis label
            plt.title(f"{entity} Distribution")  # Set title
            plt.tight_layout()  # Adjust layout
            st.pyplot(plt)  # Display plot
            plt.close()  # Close the plot to prevent persistence
        chart_count += 1  # Increment chart counter

        with table_cols[table_count % 2]:  # Alternate between table columns
            st.subheader(f"Items bought with '{selected_entity}' ({entity}) (Frequency, Support, Confidence, Lift, and Conviction):")  # Subheader for table
            st.write(df)  # Display dataframe
        table_count += 1  # Increment table counter

    st.markdown("---")  # Add a horizontal rule to separate charts and tables
