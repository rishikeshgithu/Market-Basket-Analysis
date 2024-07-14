import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go

# Function definitions from the second code snippet

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

# Set page layout to wide
st.set_page_config(layout="wide")

# Read the data
@st.cache_data
def load_data():
    data = load_data("Sample_Transaction_Data.xlsx")
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

# Calculate frequencies and supports
sku_name_counts, brand_name_counts, category_counts = count_frequencies(data)
total_transactions = data['receipt_id'].nunique()

# Select antecedent
antecedent_type = 'sku_name'
selected_antecedent = 'Prod_1'

# Count frequencies of antecedent
antecedent_frequency = data[data[antecedent_type] == selected_antecedent].shape[0]

# Calculate antecedent support
antecedent_support = antecedent_frequency / total_transactions

# Calculate support for items bought with antecedent
items_bought_with_antecedent = count_items_bought_with_antecedent(data, antecedent_type, selected_antecedent)
sku_name_bought_with_support = calculate_support(items_bought_with_antecedent['sku_name'], total_transactions)
brand_name_bought_with_support = calculate_support(items_bought_with_antecedent['brand_name'], total_transactions)
category_bought_with_support = calculate_support(items_bought_with_antecedent['Category'], total_transactions)

# Print support for items bought with antecedent
for entity, support_dict in [('sku_name', sku_name_bought_with_support), ('brand_name', brand_name_bought_with_support), ('Category', category_bought_with_support)]:
    print(f"\nSupport of {entity} bought with '{selected_antecedent}':")
    for item, support in support_dict.items():
        print(f"{item}: {support:.20f}")

# Display antecedent support
st.subheader(f"Antecedent Support of '{selected_antecedent}':")
st.write(f"The antecedent support of '{selected_antecedent}' is: {antecedent_support:.2%}")

# Display gauge chart for antecedent support
fig = go.Figure(go.Indicator(
    mode="gauge+number",
    value=antecedent_support * 100,
    title={'text': "Percentage of transactions this entity bought alongside others"},
    gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "green"}},
))
st.plotly_chart(fig)

# Display charts and tables
chart_cols = st.columns(2)
table_cols = st.columns(2)

for entity, support_dict in [('sku_name', sku_name_bought_with_support), ('brand_name', brand_name_bought_with_support), ('Category', category_bought_with_support)]:
    df = pd.DataFrame.from_dict(support_dict, orient='index', columns=['Support'])
    df = df.sort_values(by='Support', ascending=False).head(num_items_to_show)

    with chart_cols[0]:
        st.subheader(f"{entity} Distribution (sorted by Support):")
        plt.figure(figsize=(10, 6))
        plt.barh(df.index.astype(str), df['Support'])
        plt.xlabel('Support')
        plt.ylabel(selected_antecedent)
        plt.title(f"{entity} Distribution")
        plt.tight_layout()
        st.pyplot(plt)
        plt.close()

    with table_cols[0]:
        st.subheader(f"Items bought with '{selected_antecedent}' ({entity}) (Support):")
        st.write(df)

st.markdown("---")
