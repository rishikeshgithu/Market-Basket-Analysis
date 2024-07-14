import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Read the data
@st.cache
def load_data():
    data = pd.read_excel("DS_Round_1_Assignment.xlsx")
    return data

data_load_state = st.text('Loading data...')
data = load_data()
data_load_state.text('Data loaded successfully!')

# Define Streamlit app layout
def main():
    st.title("Market Basket Analysis Dashboard")

    # Filtering options
    filter_a = st.sidebar.selectbox("Filter [a]:", ['sku_name', 'brand_name', 'Category', 'Group'])

    if filter_a:
        selected_entity = st.sidebar.selectbox(f"Select {filter_a}:", data[filter_a].unique())

        if selected_entity:
            st.sidebar.markdown("---")
            st.sidebar.subheader("Filter [b]")
            # Get unique values for Filter [b] based on selection from Filter [a]
            filter_b_values = data[data[filter_a] == selected_entity]['sku_name'].unique()
            selected_entity_b = st.sidebar.selectbox(f"Select Filter [b]:", filter_b_values)

            # Filter data based on selected options
            filtered_data = data[(data[filter_a] == selected_entity) & 
                                 (data['sku_name'] == selected_entity_b)]

            # Display filtered data
            st.subheader("Filtered Data")
            st.write(filtered_data)

            # Output Charts
            st.subheader("Output Charts")

            # Chart 1: Scorecard displaying the percentage of baskets where the selected entity is bought alongside any other item
            basket_count = len(data['basket_id'].unique())
            baskets_with_entity = len(filtered_data['basket_id'].unique())
            percentage_baskets_with_entity = (baskets_with_entity / basket_count) * 100
            st.write(f"Percentage of baskets where {selected_entity_b} is bought alongside any other item: {percentage_baskets_with_entity:.2f}%")

            # Chart 2: Bar charts visualizing 'associated basket score' for sku_name, brand_name, Category, and Group
            associated_scores = filtered_data.groupby([filter_a])[['spend']].sum().reset_index()
            associated_scores.sort_values(by='spend', ascending=False, inplace=True)

            for col in ['sku_name', 'brand_name', 'Category', 'Group']:
                if col in associated_scores.columns:
                    st.subheader(f"Bar Chart for {col}")
                    plt.figure(figsize=(10, 6))
                    plt.bar(associated_scores[col], associated_scores['spend'])
                    plt.xlabel(col)
                    plt.ylabel('Associated Basket Score')
                    plt.title(f'{col} Associated Basket Score')
                    plt.xticks(rotation=45, ha='right')
                    st.pyplot(plt)

if __name__ == "__main__":
    main()
