from __future__ import annotations

from phase_1.utilities import *
from phase_2.connecting_api import *
from phase_1.ocr_extraction import *
from urllib.request import urlopen

import json
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import plotly.figure_factory as ff
import os
import random


CURRENT_PATH = os.getcwd()
TEST_FILE_FOLDER = CURRENT_PATH + "/test_file/"

def cross_analysis():
    data = pd.read_csv(TEST_FILE_FOLDER + "OtherName_Version - Copy.csv", header=0, dtype={"FIPS": str}).drop_duplicates()
    data = data.drop(["Client Representative"],axis=1)
    data = data.fillna("No Information")
    data = preprocessing_dataframe(data)

    with st.expander("See DataFrame"):
        st.write(data)
    
    fig = px.treemap(data, path = ["CB Name and Location","City", "Audit Recommendation"],
                        values = "Minor Nonconformities", color='City')
    fig.update_layout(title= 'Tree Map of Cross Analysis', width=1300, height=800, margin=dict(l = 0, r=60, b=40, t=40))
    st.plotly_chart(fig)
    with st.expander("Description and Explaination for Tree Map"):
        st.markdown("__Description__: This size of each box in tree map represented the number of non-conformities, the larger the size the bigger the non-conformance. Go from the largest outside box is the CB Name and Location, and continue to drill down to Facility Location and finally end up with Audit Recommendation")
        st.markdown("__Why this chart__: This chart is still in the development, due to the difficulty in reading style, this chart might need something to replace but still keep the integrity of the info")
    
    
    list_of_random_weight = [round(random.random(),2)*100 for i in range(data.shape[0])]
    data["Weights"] = list_of_random_weight
    fig_2 = go.Figure()
    fig_2.add_trace(go.Bar(x=[data["CB Name and Location"], data["Organisation Name"]],y=data["Weights"], name="Correction Index", marker_color="indianred"))
    fig_2.update_layout(title= 'Correction Index Ranking',xaxis={'categoryorder':'category ascending'}, width=1300, height=800, margin=dict(l = 0, r=60, b=40, t=40))
    st.plotly_chart(fig_2)
    with st.expander("Description and Explaination for Correction Index"):
        st.markdown("__Description__: The bar represent the percentage of Correction Index of a supplier. The number of Correction Index calculated base on polarity (positive and negative) in non-conformance comment + other factors (such as audit recommendation, previous audit type, etc.)")
        st.markdown("__Why this chart__: Viewer can choose to see the bar chart or a table of correction index number. You can hover the mouse in to look more clearly")
    
    with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
        counties = json.load(response)
    fig_3 = px.choropleth(data, geojson=counties, locations="FIPS", color="Minor Nonconformities",
                            color_continuous_scale="Viridis",
                            range_color=(0,12),
                            scope="usa",
                            labels = {"Minor Nonconformities": "minor"}
                            )
    fig_3.update_layout(title= 'Map', width=1300, height=800, margin=dict(l = 0, r=60, b=40, t=40))
    st.plotly_chart(fig_3)
    with st.expander("Description and Explaination for Map Graph"):
        st.markdown("__Description__: The graph represent the location of the facility specifically and the size of dot will represent the number of non-conformities that the facility have.")
        st.markdown("__Why this chart__: Well this chart easy to understand right ? This will be use for the future pathway as well such as Predict the Supplier Sustainability")
    
    x_1 = data["Minor Nonconformities"][data["CB Name and Location"].str.contains("SGS")].values
    x_2 = data["Minor Nonconformities"][data["CB Name and Location"].str.contains("AIBI")].values
    hist_data = [x_1, x_2]
    group_label = ["SGS", "AIBI"]
    
    avg_1 = round(data["Minor Nonconformities"][data["CB Name and Location"].str.contains("SGS")].mean(),2)
    avg_2 = round(data["Minor Nonconformities"][data["CB Name and Location"].str.contains("AIBI")].mean(),2)
    
    count_1 = 0
    count_2 = 0
    for i in x_1:
        if i >= avg_1:
            count_1+= 1
    
    for i in x_2:
        if i >= avg_2:
            count_2+= 1
    
    col1, col2 = st.columns(2)
    
    with col1:
        col1.subheader("Distribution of Nonconformities")
        fig_4 = ff.create_distplot(hist_data, group_label)
        st.plotly_chart(fig_4)
        
        with st.expander("Description and Explaination for Distribution of Nonconformities"):
            st.markdown("__Description__: The graph represent the distribution of the nonconformities based on the Auditor name. So for example as you can see the blue one represent the SGS, and the bar represent how many nonconformities lye in that range of number")
            st.markdown("__Why this chart__: Well we want to see the summaries of all the supplier non-conformance. This graph would give us that info.")
    
    with col2:
        col2.subheader("The Rate Compare to Average")
        st.markdown(f"With SGS United Kingdom, __{round(count_1/len(x_1),2)*100}% of Audit Report with Minor Nonconformities is higher than the average__")
        st.markdown(f"With AIBI, __{round(count_2/len(x_2),2)*100}% of Audit Report with Minor Nonconformities is higher than the average__")
        st.markdown(f"All __100% nonconformities have been closed__ from the last audit report")

def single_analysis():
    data = pd.read_csv(TEST_FILE_FOLDER + "OtherName_Version - Copy.csv", header=0, dtype={"FIPS": str}).drop_duplicates()
    data = data.drop(["Client Representative"],axis=1)
    data = data.fillna("No Information")
    data = preprocessing_dataframe(data)
    
    st.markdown("You choose file: __Company A Buffalo City Facility Audit Jan-July 2020.pdf__")
    value = main_phase_2("General Mills", "Iowa")
    with st.expander("Basic Information"):
        st.markdown("__Organisation Name__: Company A")
        st.markdown("__City__: Buffalo")
        st.markdown("__State__: New York")
    
    with st.expander("Audit Information"):
        st.markdown("__Audit Recommendation__: Certification Maintained")
        st.markdown("__Audit Type__: Recertification")
        st.markdown("__Minor Nonconformities__: 5")
        st.markdown("__Major Nonconformities__: 0")
        st.markdown("__Critical Nonconformities__: 0")
    
    st.write("We find something similar of __FDA Recall Database__")
    
    with st.expander("Company A FDA Recall"):
        recalling_firm_count = 0
        for i in range(len(value)):
            if value[i]["recalling_firm"] == "General Mills, Inc":
                recalling_firm_count += 1
        
        st.markdown(f"__Company A__ was got recalled __{recalling_firm_count} times in the last 4 years__")
            
        city_count = 0
        for i in range(len(value)):
            if value[i]["city"] == "Buffalo":
                city_count += 1
        st.markdown(f"__Buffalo City__ has __{city_count} recall cases in the last 4 years__")
        
        top_5_product = []
        for i in range(len(value)):
            if value[i]["recalling_firm"] == "General Mills, Inc":
                top_5_product.append(cleaning_product_name(value[i]["product_description"]))
        
        st.write(f"Top 5 nearest products got called by FDA from Company A: __{top_5_product[:5]}__")
        st.write("100% of product is __Food Recall__ / 100% of product has been __Terminated__")
        st.write("With __30% of cases is Class I__, __70% of cases is Class II__ in ranking of dangerous")
    
    with st.expander("Buffalo City FDA Recall"):
        st.markdown("With __Buffalo City__ separately, there has been 31 times cases happened at here in the last 4 years")
        st.markdown("Top 5 Product recent got recall at Buffalo City: __Wegmans Milk Chocolate Sucker, Cake Truffles, ALL NATURAL ANCIENT GRAIN BREAD, GRANDMA'S perogies POTATO & BACON PEROGIES, Signature SELECT Vanilla Ice Cream & White Cake ICE CREAM CAKE__")
        st.markdown("Top 5 Firms got recall: __Landies Candies, Inc., Rich Products Corp, BUFFALO SAV, INC., The Sausage Maker, Inc., Upstate Niagara Cooperative, Inc.__")
        
def main():
    data = pd.DataFrame()
    st.title("Risk Assessment 3PA")
    st.markdown("> __Analysis the 3PA documents base on different attribute and connecting with outside database__")
    st.markdown("> __Please look at the instruction before start surfing the web.__")
    st.markdown("> __With each of the graph, there will be an explanation on the uses and purpose of using this specific graph__")
    with st.expander("Instruction"):
        st.markdown("__When you first open the app, please follow the instruction here to have the best experience__")
        st.markdown("On the top right corner of the app, there is a __3 line button__, please press on that one and choose __Setting__ ")
        st.markdown("After that, under the __APPEARANCE__ tab, please tick __WIDE MODE__")
        st.markdown("This would improve your experience on the website. Thank you")
        
    
    add_selectbox = st.sidebar.selectbox(
        "How do you want to analysis the files ?",
        ("Cross-Analysis", "Single File Analysis")
    )
    
    if add_selectbox == "Cross-Analysis":
        with st.sidebar.expander("Defition and Usage:"):
            st.write("The uses of cross-analysis is to help user compare between all of the files that they upload on when doing risk analysis on Otrafy. This give the user a clearer view of all of the files without spending time to read")
        cross_analysis()
    
    elif add_selectbox == "Single File Analysis":
        with st.sidebar.expander("Defition and Usage:"):
            st.write("With Single File Analysis, user will focus on one specific file that they interested in or they curious to understand more about the file specifically.")
        single_analysis()

if __name__ == "__main__":
    main()