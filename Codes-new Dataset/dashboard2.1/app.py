import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from collections import Counter
import plotly.express as px
st.set_page_config(layout="wide")

backgroundcolor = """

"""
tab1, tab2 = st.tabs(["Item Distribution", "Spend Distribution"])
st.markdown(backgroundcolor, unsafe_allow_html=True)

with tab1:  
    df = pd.read_excel('Sample_Transaction_Data.xlsx')
    with st.container():
        col1, col2, col3 = st.columns([1,1,1])
        with col1:
            filter_option = st.selectbox('choose and option:', ["MFG", "sku_name", "brand_name", "Category", "Group"])
           
        with col2:
            selected_entity = st.selectbox("Choose a value for the selected option:", df[filter_option].unique())
            slider_select = st.slider('Number of Products to show', min_value=1, max_value=20, value=10)
        with col3:
            selected_region = st.multiselect("Choose the Region:", df['Region'].unique())
    dummydf = df[df[filter_option] == selected_entity]
    dfwithregion = dummydf[dummydf['Region'].isin(selected_region)]
    selected_df = dfwithregion['receipt_id'].unique()   #all receipt id where the selected entity exits

    num_of_baskets_with_entity = df[df[filter_option] == selected_entity]['receipt_id'].nunique() #number of reciepts where the entity exits

    basket_frequency_Df = (df[df['receipt_id'].isin(selected_df)])        

    final_df = basket_frequency_Df[basket_frequency_Df[filter_option] != selected_entity]

    no_of_times_diff_item_bought = final_df['receipt_id'].nunique() #no of times selected entity was bought along other item
    percentage = round(( no_of_times_diff_item_bought/ num_of_baskets_with_entity) * 100, 2)

    with st.container():
        col4,col5,col6 = st.columns([1,1,1])
        with col4:
            fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = percentage,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title="percentage plot"))
            st.plotly_chart(fig, use_container_width=True)
            
            
        with col5:
            df_skuname = pd.DataFrame(final_df['sku_name'].value_counts())
            df_skuname['sku_name']= df_skuname.index  
            df_skuname['percentage'] = (df_skuname['count']/no_of_times_diff_item_bought)*100
            final_df_skuname=df_skuname.head(slider_select)
            fig2 = px.bar(final_df_skuname, x='percentage', y='sku_name', orientation='h',title="PLOT 1",height=500)
            fig2.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig2, use_container_width=True)

        with col6:
            df_brandname = pd.DataFrame(final_df['brand_name'].value_counts())
            df_brandname['brand_name']= df_brandname.index
            df_brandname['percentage'] = (df_brandname['count']/no_of_times_diff_item_bought)*100
            final_df_brandname=df_brandname.head(slider_select)
            fig3 = px.bar(final_df_brandname, x='percentage', y='brand_name', orientation='h',title="PLOT 2",height=500)
            fig3.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig3, use_container_width=True )

        with col5:
            df_category = pd.DataFrame(final_df['Category'].value_counts())
            df_category['Category']= df_category.index
            final_df_category = df_category.head(slider_select)
            df_category['percentage'] = (final_df_category['count']/no_of_times_diff_item_bought)*100   
            fig4 = px.bar(df_category, x='percentage', y='Category', orientation='h',title="PLOT 3",height=500)
            fig4.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig4, use_container_width=True )
with tab2:
    with st.container():
        col1, col2, col3 = st.columns([1,1,1])
        with col1:
            filter_option2 = st.selectbox('choose and option:', ["MFG", "sku_name", "brand_name", "Category", "Group"], key=1)
        with col2:
            selected_entity2 = st.selectbox("Choose a value for the selected option:", df[filter_option2].unique(),key=2)
        with col3:
            selected_region2 = st.multiselect("Choose the Region:", df['Region'].unique(),key=3)
        
    with st.container():
        col4, col5, col6 = st.columns([1,1,1])
        df['day_of_week'] = df['Date'].dt.dayofweek
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        df['day_of_week'] = df['day_of_week'].apply(lambda x: day_names[x])
        df['date_of_month']=df['Date'].dt.day
        dummydf1 = df[df[filter_option2]==selected_entity2][df['Region'].isin(selected_region2)]

        with col4:
            spend_timeofday = dummydf1[['Hour', 'receipt_value_usd']].groupby('Hour')['receipt_value_usd'].sum().round(2)
            df_spend_timeofday = pd.DataFrame(spend_timeofday)
            df_spend_timeofday['Hour']= df_spend_timeofday.index
            total_receipt_val_ofday =df_spend_timeofday['receipt_value_usd'].sum().round(2)
            df_spend_timeofday['percentage']= (df_spend_timeofday['receipt_value_usd']/total_receipt_val_ofday)*100 
            fig5 = px.bar(df_spend_timeofday, x='percentage', y='Hour', orientation='h',title="PLOT 1",height=500)
            fig5.update_yaxes(autorange="reversed")
            fig5.update_layout(yaxis_range=[0,23],yaxis={"dtick":1})
            st.plotly_chart(fig5, use_container_width=True)
            
        with col5:
            spend_weekday = dummydf1[['day_of_week', 'receipt_value_usd']].groupby('day_of_week')['receipt_value_usd'].sum().round(2)
            df_weekday = pd.DataFrame(spend_weekday)
            df_weekday['day_of_week'] = df_weekday.index
            total_receipt_val_ofweek =df_weekday['receipt_value_usd'].sum().round(2)
            df_weekday['percentage']=(df_weekday['receipt_value_usd']/total_receipt_val_ofweek)*100
            day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            weekly_sales_sorted = df_weekday.set_index('day_of_week').reindex(day_order).reset_index().fillna(0) 
            fig6 = px.bar(weekly_sales_sorted, x='percentage', y='day_of_week', orientation='h',title="PLOT 2",height=500)
            fig6.update_yaxes(autorange="reversed")
            st.plotly_chart(fig6, use_container_width=True)
        
        with col6:
            spend_date = dummydf1[['date_of_month', 'receipt_value_usd']].groupby('date_of_month')['receipt_value_usd'].sum().round(2)
            df_date = pd.DataFrame(spend_date)
            df_date['date_of_month']= df_date.index                       
            total_receipt_val_ofmonth =df_date['receipt_value_usd'].sum().round(2)
            df_date['percentage']=(df_date['receipt_value_usd']/total_receipt_val_ofmonth)*100
            fig7 = px.bar(df_date, x='percentage', y='date_of_month', orientation='h',title="PLOT 3",height=500)
            fig7.update_yaxes(autorange="reversed")
            fig7.update_layout(yaxis_range=[1,31],yaxis={"dtick":1})
            st.plotly_chart(fig7, use_container_width=True)

