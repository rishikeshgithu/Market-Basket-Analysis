import streamlit as st
import pandas as pd

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
        'Category': {}
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
@st.cache  # Cache the data loading function to improve performance
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
    filter_a = st.selectbox("Filter [a]:", ['sku_name', 'brand_name', 'Category'])

with col2:
    if filter_a:
        selected_entity = st.selectbox(f"Filter [b]: Select {filter_a}:", data[filter_a].unique())

with col3:
    sort_by = st.selectbox("Sort by:", ['Support', 'Confidence', 'Lift', 'Conviction'])

with col4:
    num_items_to_show = st.slider('Number of Items to Show:', min_value=1, max_value=20, value=10)

if filter_a and selected_entity and sort_by:
    antecedent_support = calculate_antecedent_support(data, filter_a, selected_entity)
    consequent_support_dict = calculate_consequent_support(data)
    items_bought_with = analyze_items_bought_with(data, filter_a, selected_entity)
    dataframes = {}

    for entity, counts in items_bought_with.items():
        df = pd.DataFrame.from_dict(counts, orient='index', columns=['Frequency'])
        df = df.sort_values(by='Frequency', ascending=False)
        total_occurrences = df['Frequency'].sum()
        df['Support'] = df['Frequency'] / total_occurrences
        df['Confidence'] = df['Frequency'] / (antecedent_support * total_occurrences)
        df['Lift'] = df.apply(lambda row: row['Frequency'] / (antecedent_support * consequent_support_dict.get(row.name, 0.0001) * total_occurrences), axis=1)
        df['Conviction'] = df.apply(lambda row: max((1 - consequent_support_dict.get(row.name, 0.0001)) / (1 - row['Confidence']), 0), axis=1)
        df = df.sort_values(by=sort_by, ascending=False).head(num_items_to_show)
        dataframes[entity] = df

    st.subheader(f"Antecedent Support of '{selected_entity}':")
    st.write(f"The antecedent support of '{selected_entity}' is: {antecedent_support:.2%}")

    for entity, df in dataframes.items():
        st.subheader(f"Items bought with '{selected_entity}' ({entity}) (Frequency, Support, Confidence, Lift, and Conviction):")
        st.write(df)
