# streamlit_app.py

import streamlit as st
import mysql.connector
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from bokeh.transform import dodge
from bokeh.palettes import magma
from st_aggrid import AgGrid, GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode
from bokeh.plotting import figure,output_file ,show
from bokeh.models import ColumnDataSource,HoverTool
import math
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from annotated_text import annotated_text
from bokeh.io import curdoc





from sqlalchemy import create_engine
engine= create_engine("mysql+mysqldb://root:rootpass@localhost:3306/fire_data")



Incidents=pd.read_sql("SELECT * FROM Incidents",con=engine)
violations_lens = pd.read_sql("SELECT * FROM lens_on_violations",con=engine).set_index('zipcode')
lens_on_violations1= pd.read_sql("SELECT * FROM lens_on_violations",con=engine)
lens_on_violations = pd.read_sql("SELECT * FROM lens_on_violations",con=engine)
lens_on_violations2=pd.read_sql("SELECT * FROM lens_on_violations",con=engine).drop_duplicates(subset=['violation item description']).set_index('violation item description')
Incidents2=pd.read_sql("SELECT * FROM Incidents",con=engine).set_index('neighborhood_district')


st.set_page_config(layout="wide")

# Print results.
def aggrid_interactive_table(df: pd.DataFrame):
    """Creates an st-aggrid interactive table based on a dataframe.

    Args:
        df (pd.DataFrame]): Source dataframe

    Returns:
        dict: The selected row
    """
    options = GridOptionsBuilder.from_dataframe(
        df, enableRowGroup=True, enableValue=True, enablePivot=True
    )

    options.configure_side_bar()

    options.configure_selection("single")
    selection = AgGrid(
        df,
        enable_enterprise_modules=True,
        gridOptions=options.build(),
        theme="light",
        update_mode=GridUpdateMode.MODEL_CHANGED,
        allow_unsafe_jscode=True,
    )

    return selection

st.markdown("""
<style>
.big-font {
    font-size:95px !important;
    text-align:left;
    font-style:italic;
    color:orangered;
}
</style><b class="big-font">San Francisco Fire Department</b>
""", unsafe_allow_html=True)



#st.markdown('<p class="big-font">Fire Department</p>',unsafe_allow_html=True)
#st.markdown("<h1 style='text-align: center; color: red;'>Fire Department</h1>", unsafe_allow_html=True)
#st.markdown("""<h1 style='text-align: center;'>Fire Department</h1>""",unsafe_allow_html=True)



lens_on_violations['zipcode']=lens_on_violations['zipcode'].astype(str)
lens_on_violations_cds=ColumnDataSource(lens_on_violations)
zip_list=list(lens_on_violations['zipcode'])
start_zip,end_zip=st.select_slider('select range of zipcodes',options=zip_list,value=(zip_list[0],zip_list[-1]))
st.write('Zipcode : ' ,start_zip,end_zip)

zip_range=zip_list[zip_list.index(start_zip):zip_list.index(end_zip)]
#Incidents=Incidents[Incidents['zipcode'].isin(zip_range)]
violations_lens = violations_lens.reset_index()[violations_lens.reset_index()['zipcode'].isin(zip_range)]
lens_on_violations1=lens_on_violations1.reset_index()[lens_on_violations1.reset_index()['zipcode'].isin(zip_range)]
#lens_on_violations =lens_on_violations.reset_index()[lens_on_violations.reset_index()['zipcode'].isin(zip_range)]
#Incidents2=Incidents2.reset_index()[Incidents2.reset_index()['zipcode'].isin(zip_range)]
print(len(zip_range))

df=pd.DataFrame(Incidents)


col1,col2=st.columns(2)

with col1:

    #st.subheader('Number of incidents by zipcode')
    st.markdown("""
    <style>
    .b-font {
        font-size:36px !important;
        font-style:italic;
        color:bisque;
    }
    </style><p class="b-font"> Number of incidents by zipcode</p>
    """, unsafe_allow_html=True)
    violations_lens1=violations_lens.drop_duplicates(subset=['zipcode']).dropna()
    violations_lens1['zipcode']=violations_lens1['zipcode'].astype(str)
    violations_lens_cds=ColumnDataSource(violations_lens1)
    Tooltips= [("zipcode","@zipcode"), ("No.In", "@num_incidents")]
    p=figure(x_range=violations_lens1['zipcode'], height=600,width=600,toolbar_location=None, tooltips=Tooltips)
    p.background_fill_color="#f5f5f5"
    #hover =p.select(dict(type=HoverTool))
    #hover.tooltips = [("zipcode","@zipcode"), ("No.In", "@$num_incidents")]
    #hover.mode = 'mouse'
    p.xaxis.major_label_orientation=math.pi/4
    p.vbar(x='zipcode',top='num_incidents',source=violations_lens_cds)
    st.bokeh_chart(p)



    ##st.subheader('Incident date by count of Incident number')
    #a1 = df.groupby("Incident Date").agg({"Incident Number":len})
    #st.line_chart(a1)


    #st.subheader('Incident date by count of Incident number')
    st.markdown("""
    <style>
    .a-font {
        font-size:36px !important;
        font-style:italic;
        color:bisque;
    }
    </style><p class="a-font">Incident date by count of Incident number</p>
    """, unsafe_allow_html=True)
    df=pd.DataFrame(Incidents)
    fig = px.line(df.groupby("Incident Date").agg({"Incident Number":len}).reset_index(), x='Incident Date', y="Incident Number")
    fig['layout'].update(height=750,width=700)
    st.plotly_chart(fig)


    #st.subheader('Time Taken for response per zipcode')
    st.markdown("""
    <style>
    .c-font {
        font-size:36px !important;
        font-style:italic;
        color:bisque;
    }
    </style><p class="c-font">Time Taken for response per zipcode</p>
    """, unsafe_allow_html=True)
    violations_lens1=violations_lens.reset_index().drop_duplicates(subset=['zipcode']).dropna()
    violations_lens1['zipcode']=violations_lens1['zipcode'].astype(str)
    violations_lens_cds=ColumnDataSource(violations_lens1)
    curdoc().theme='contrast'
    Tooltips= [("zipcode","@zipcode"), ("time difference", "@time_diff")]
    p1=figure(x_range=violations_lens1['zipcode'], height=600,width=600,tooltips=Tooltips)
    p1.xaxis.major_label_orientation=math.pi/4
    p1.vbar(x='zipcode',top='time_diff',source=violations_lens_cds)
    st.bokeh_chart(p1)


##
    #st.subheader('**Most Common Violation per zipcode**.')
    st.markdown("""
    <style>
    .d-font {
        font-size:36px !important;
        font-style:italic;
        color:bisque;
    }
    </style><p class="d-font">Most Common Violation per zipcode</p>
    """, unsafe_allow_html=True)
    DataFrame=lens_on_violations1[['zipcode','violation item description']]
    def zipcode(val):
        color = 'steelblue'
        return f'background-color: {color}'
    hide_table_row_index = """
            <style>
            tbody th {display:none}
            .blank {display:none}
            </style>
            """

# Inject CSS with Markdown
    st.markdown(hide_table_row_index, unsafe_allow_html=True)


    #st.table(DataFrame)
    st.table(DataFrame.style.applymap(zipcode, subset=['zipcode']))


#aggrid_interactive_table(df)
#aggrid_interactive_table(violations_lens)

with col2:

    #st.subheader('Number of violations by zipcode')
    st.markdown("""
    <style>
    .g-font {
        font-size:36px !important;
        font-style:italic;
        color:bisque;
    }
    </style><p class="g-font">Number of violations by zipcode</p>
    """, unsafe_allow_html=True)
    violations_lens1=violations_lens.reset_index().drop_duplicates(subset=['zipcode']).dropna()
    violations_lens1['zipcode']=violations_lens1['zipcode'].astype(str)
    violations_lens_cds=ColumnDataSource(violations_lens1)
    Tooltips= [("zipcode","@zipcode"), ("No.Vio", "@num_violations")]
    #hover = p.select(dict(type=HoverTool))
    #hover.tooltips = [("zipcode","@zipcode"), ("No.Vio", "@$num_violations")]
    #hover.mode = 'mouse'
    p=figure(x_range=violations_lens1['zipcode'],tooltips=Tooltips,height=600,width=600)
    p.xaxis.major_label_orientation=math.pi/4
    p.vbar(x='zipcode',top='num_violations',source=violations_lens_cds)
    st.bokeh_chart(p)




#
    #st.subheader('Number of incidents & Number of violations by zipcode')
    st.markdown("""
    <style>
    .f-font {
        font-size:31px !important;
        font-style:italic;
        color:bisque;
    }
    </style><p class="f-font">Number of incidents & Number of violations by zipcode</p>
    """, unsafe_allow_html=True)
    violations_lens1=violations_lens.reset_index().drop_duplicates(subset=['zipcode']).dropna()
    violations_lens1['zipcode']=violations_lens1['zipcode'].astype(str)
    trace1=go.Bar(
           x=violations_lens1['zipcode'],
           y=violations_lens1['num_incidents'],
           name='Num of Incidents',
           marker=dict(
                color='rgb(34,163,192)'
                      )
           )
    trace2=go.Scatter(
        x=violations_lens1['zipcode'],
        y=violations_lens1['num_violations'],
        name='Num of Violations',
        yaxis='y2'
    )
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(trace1)
    fig.add_trace(trace2,secondary_y=True)
    fig['layout'].update(height = 750, width = 750,xaxis=dict(
          tickangle=-90
        ))
    st.plotly_chart(fig)



 #####
    #st.subheader('Violations with violation item description')
    st.markdown("""
    <style>
    .e-font {
        font-size:36px !important;
        font-style:italic;
        color:bisque;
    }
    </style><p class="e-font">Violations with violation item description</p>
    """, unsafe_allow_html=True)
    violations_lens_cds=ColumnDataSource(lens_on_violations2)
    output_file("dark_minimal.html")
    curdoc().theme = 'dark_minimal'
    Tooltips= [("violation item description","@violation item description"), ("No.Vio", "@num_violations")]
    p=figure(x_range=list(lens_on_violations2.index),width=600, height=600, tooltips=Tooltips)
    p.xaxis.major_label_orientation=math.pi/4
    p.vbar(x='violation item description',top='num_violations',source=violations_lens_cds)
    st.bokeh_chart(p)


    #st.subheader('Number of incidents by Number of violations ')
    #a5=lens_on_violations[['num_violations','num_incidents']]
    #st.line_chart(a5)
    #st.subheader('Number of incidents by Number of violations ')
    st.markdown("""
    <style>
    .d-font {
        font-size:36px !important;
        font-style:italic;
        color:bisque;
    }
    </style><p class="d-font">Number of incidents by Number of violations</p>
    """, unsafe_allow_html=True)
    violations_lens1=lens_on_violations.reset_index().drop_duplicates(subset=['zipcode']).dropna()
    violations_lens1['zipcode']=violations_lens1['zipcode'].astype(str)
    violations_lens1.sort_values(by = ['num_violations'], ascending = True, inplace = True)
    violations_lens_cds=ColumnDataSource(violations_lens1)
    Tooltips= [("No.vio","@num_violations"), ("No.In", "@num_incidents")]
    #hover = p.select(dict(type=HoverTool))
    #hover.tooltips = [("No.vio","@$num_violations"), ("No.In", "@$num_incidents")]
    #hover.mode = 'mouse'
    p3=figure(width=600, height=920, tooltips=Tooltips)
    p3.xaxis.major_label_orientation=math.pi/4
    p3.line(x='num_violations',y='num_incidents',source=violations_lens_cds)
    st.bokeh_chart(p3)
