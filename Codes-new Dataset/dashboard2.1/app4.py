import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Set page layout to wide
st.set_page_config(layout="wide")

# Function to calculate antecedent support
def calculate_antecedent_support(data, item_type, selected_item):
    transactions_with_item = data[data[item_type] == selected_item]['receipt_id'].nunique()
    total_transactions = data['receipt_id'].nunique()
    antecedent_support = transactions_with_item / total_transactions
    return antecedent_support

# Function to calculate consequent support for each product
def calculate_consequent_support(data):
    total_transactions = data['receipt_id'].nunique()
    support_dict = {}
    for product in data['sku_name'].unique():
        transactions_with_product = data[data['sku_name'] == product]['receipt_id'].nunique()
        support = transactions_with_product / total_transactions
        support_dict[product] = support
    return support_dict

# Function to analyze items bought along with a specified item
def analyze_items_bought_with(data, item_type, selected_item):
    selected_item_data = data[data[item_type] == selected_item]
    selected_item_receipt_ids = selected_item_data['receipt_id'].unique()
    items_bought_with = {
        'sku_name': {},
        'brand_name': {},
        'Category': {},
        'Group': {}
    }
    for receipt_id in selected_item_receipt_ids:
        receipt_data = data[data['receipt_id'] == receipt_id]
        receipt_data = receipt_data[receipt_data[item_type] != selected_item]
        for entity in items_bought_with.keys():
            entities = receipt_data[entity].unique()
            for item in entities:
                if item in items_bought_with[entity]:
                    items_bought_with[entity][item] += 1
                else:
                    items_bought_with[entity][item] = 1
    return items_bought_with

# Read the data
@st.cache_data
def load_data():
    data = pd.read_excel("Sample_Transaction_Data.xlsx")
    return data

# Display a loading spinner while loading data
with st.spinner('Loading data...'):
    data = load_data()

# Page title
st.title('Market Basket Analysis with Apriori Algorithm')

# Horizontal layout for filters
col1, col2, col3, col4 = st.columns(4)

with col1:
    # Dropdown for selecting the entity type
    filter_a = st.selectbox("Filter [a]:", ['sku_name', 'brand_name', 'Category', 'Group'])

with col2:
    if filter_a:
        # Based on the selection from Filter [a], display a second dropdown menu showing all unique values for the selected entity
        selected_entity = st.selectbox(f"Filter [b]: Select {filter_a}:", data[filter_a].unique())

with col3:
    # Dropdown for selecting the sorting criterion
    sort_by = st.selectbox("Sort by:", ['Support', 'Confidence', 'Lift', 'Conviction'])

with col4:
    # Slider for selecting the number of items to show
    num_items_to_show = st.slider('Number of Items to Show:', min_value=1, max_value=20, value=10)

if filter_a and selected_entity and sort_by:
    antecedent_support = calculate_antecedent_support(data, filter_a, selected_entity)
    consequent_support_dict = calculate_consequent_support(data)
    items_bought_with = analyze_items_bought_with(data, filter_a, selected_entity)
    dataframes = {}

    for entity, counts in items_bought_with.items():
        df = pd.DataFrame.from_dict(counts, orient='index', columns=['Frequency'])
        df = df.sort_values(by='Frequency', ascending=True)  # Sort in ascending order
        total_occurrences = df['Frequency'].sum()
        df['Support'] = (df['Frequency'] / total_occurrences) * 100
        df['Confidence'] = df['Frequency'] / (antecedent_support * total_occurrences)
        df['Lift'] = df.apply(lambda row: row['Frequency'] / (antecedent_support * consequent_support_dict.get(row.name, 0.0001) * total_occurrences), axis=1)
        df['Conviction'] = df.apply(lambda row: (1 - consequent_support_dict.get(row.name, 0.0001)) / (1 - row['Confidence']), axis=1)
        df = df.sort_values(by=sort_by, ascending=False).head(num_items_to_show)
        dataframes[entity] = df

    st.subheader(f"Antecedent Support of '{selected_entity}':")
    st.write(f"The antecedent support of '{selected_entity}' is: {antecedent_support:.2%}")

    # Display bar charts in a 2x2 grid with horizontal bars
    chart_cols = st.columns(2)
    chart_count = 0
    for entity, df in dataframes.items():
        with chart_cols[chart_count % 2]:
            st.subheader(f"{entity} Distribution (sorted by {sort_by}):")
            sorted_df = df.sort_values(by=sort_by, ascending=True)  # Sort by the selected criterion
            plt.figure(figsize=(10, 6))
            plt.barh(sorted_df.index.astype(str), sorted_df[sort_by])  # Horizontal bar chart
            plt.xlabel(sort_by)
            plt.ylabel(selected_entity)
            plt.title(f"{entity} Distribution")
            plt.tight_layout()
            st.pyplot(plt)
        chart_count += 1

    st.markdown("---")  # Add a horizontal rule to separate charts and tables

    # Display data tables in a 2x2 grid
    table_cols = st.columns(2)
    table_count = 0
    for entity, df in dataframes.items():
        with table_cols[table_count % 2]:
            st.subheader(f"Items bought with '{selected_entity}' ({entity}) (Frequency, Support, Confidence, Lift, and Conviction):")
            st.write(df)
        table_count += 1
