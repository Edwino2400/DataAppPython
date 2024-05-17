# -*- coding: utf-8 -*-
"""
Created on Tue Oct 24 10:50:55 2023

@author: Edwin Chigara
"""

import numpy as np
import pandas as pd
import streamlit as st
from PIL import Image
import io
import os
import base64
from datetime import datetime
import SessionState
import csv
import re


# file_path= "D:/DEV/Python projects/agribank-data-analyser/"
file_path = ".\"
img = Image.open(os.path.join(file_path, 'dataapp.png'))
# this should the first thing to do before you run anything else

st.set_page_config(page_title='Edwin | DATA APP', page_icon=img, layout="wide", initial_sidebar_state="expanded")

# cocde to check turn of setting and footer
# st.markdown(""" <style>
# MainMenu {visibility: hidden;}
# footer {visibility: hidden;}
# </style> """, unsafe_allow_html=True)

encoding = "utf-8"


# @st.cache(allow_output_mutation=True)
def dataframe_finder(file):
    if file is not None:
        try:
            if file.name[-3:] == 'csv' or file.name[-3:] == 'txt':
                try:

                    # df_data = pd.read_csv(file,dtype=str,quotechar ="'",skipinitialspace=True,quoting=csv.QUOTE_MINIMAL)
                    # df_data.replace("'",'',inplace=True)
                    file.seek(0)
                    df_data = pd.concat((chunk for chunk in
                                         pd.read_csv(io.StringIO(file.read().decode('utf-8')), dtype=str, quotechar='"',
                                                     skipinitialspace=True, quoting=csv.QUOTE_MINIMAL,
                                                     chunksize=10000)))
                    df_data.replace('"', '', inplace=True)


                except:
                    file.seek(0)
                    # df_data = pd.read_csv(io.StringIO(file.read().decode('utf-8')), sep='[;,|]',engine='python',dtype=str)
                    df_data = pd.concat((chunk for chunk in
                                         pd.read_csv(io.StringIO(file.read().decode('ISO-8859-1')), sep='[;,|]',
                                                     engine='python', dtype=str)))
                    df_data.replace('"', '', inplace=True)

            else:
                df_data = pd.read_excel(file)

            return df_data

        except Exception as e:
            st.error(e)



def float_converter(x):
    try:
        return float(x)
    except ValueError:
        return None



def get_table_download_link(df, file_type, btn_name):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    filename = btn_name + "_" + str(datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p"))
    if file_type == 'csv':
        file_name = filename + ".csv"
        csv = df.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
        href = f'<a href="data:file/csv;base64,{b64}" download="{file_name}"><button class="btn btn-success"><i class="fa fa-download"></i> {btn_name}</button></a>'

    elif file_type == 'excel':
        file_name = filename + ".xlsx"
        val = to_excel(df)
        b64 = base64.b64encode(val)  # val looks like b'...'
        href = f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="{file_name}"><button class="btn btn-success"><i class="fa fa-download"></i> {btn_name}</button></a>'  # decode b'abc' => abc

    return href


def to_excel(df):
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')  # <--- here
    writer.save()
    processed_data = output.getvalue()

    return processed_data


def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
        # local_css("style.css")


def remote_css(url):
    st.markdown(f'<link href="{url}" rel="stylesheet">', unsafe_allow_html=True)
    # remote_css('https://fonts.googleapis.com/icon?family=Material+Icons')


def icon(icon_name):
    st.markdown(f'<i class="material-icons">{icon_name}</i>', unsafe_allow_html=True)
    # icon("search")


@st.cache(allow_output_mutation=True)
def choice_download_dup(choice):
    if choice == "KEEP FIRST RECORD OF THE DUPLICATE":
        download = 'first'
    elif choice == "KEEP LAST RECORD OF THE DUPLICATE":
        download = "last"
    else:
        download = False

    return download


def main():
    st.markdown(
        """
        <style>
            .stProgress > div > div > div > div {
                background-color: #1c4b27;
            }
        </style>""",
        unsafe_allow_html=True,
    )

    st.balloons()

    
    col1, mid, col2 = st.columns([1,1,20])
    with col1:
        st.sidebar.image(img,width=70)
    with col2:
        st.sidebar.subheader("DATA APP")

    menu = ["V_LOOK UP","DUPLICATES REMOVER"]
    choice = st.sidebar.selectbox("Menu",menu)

    if choice =='V_LOOK UP':
        #row one columns
        st.title('V-LOOK UP')
        #st.header('Select your files here')
        st.markdown("""> This application has been designed so as to improve efficiency in analysing and comparing data between two files""")

        col1,col2 = st.columns(2)
        with col1:
            st.header('File One')
            uploaded_file = st.file_uploader("Upload your input File One here", type=["csv","xlsx","txt"])
        with col2:
            st.header('File Two')
            uploaded_file_1 = st.file_uploader("Upload your input File Two here", type=["csv","xlsx","txt"])

        if (uploaded_file is not None) or (uploaded_file_1 is not None):
            st.header('Select your primary key in each file and run report')

        #row two columns
        col3,col4,col5 = st.columns((1, 1, 1))

        if uploaded_file is not None:
            with col3:
                if uploaded_file is not None:
                    primary_left=st.selectbox('Primary column of File one', (dataframe_finder(uploaded_file).columns.values.tolist()))

            with col4:
                if (uploaded_file is not None) or (uploaded_file_1 is not None):
                    join_type=st.selectbox('Type of Join', ('inner', 'left', 'right','outer'))

            with col5:
                if uploaded_file_1 is not None:
                    primary_right=st.selectbox('Primary column of File two', (dataframe_finder(uploaded_file_1).columns.values.tolist()))

        if (uploaded_file is not None) or (uploaded_file_1 is not None):
            st.markdown("> Do you want any help in understanding the types of joins used above?")
            expander = st.expander("Click Here for Help")
            with expander:
                c1, c2, c3, c4 = st.columns((1, 1, 1, 1))
                try:
                    with c1:
                        #inner join
                        c1_image=Image.open(os.path.join(file_path,'inner.png'))
                        st.image(c1_image,width=160,caption='inner join')
                        st.markdown(""" 
                                    **Inner Join**

                                    `Inner Join` returns records that have matching values in both tables 

                                    **Note:** The `INNER JOIN` keyword selects all rows from both tables as long
                                    as there is a match between the columns.""")
                    with c2:
                        #left join
                        c2_image=Image.open(os.path.join(file_path,'left.png'))
                        st.image(c2_image,width=150,caption='left join')
                        st.markdown(""" 
                                    **Left Join**

                                    `Left Join` returns all records from the left table, and the matched records from the right table

                                    **Note:** The `LEFT JOIN` keyword returns all records from the left table (table1), and the matching records from the right table (table2). The result is 0 records from the right side, if there is no match.
                                    """)

                    with c3:
                        #right join
                        c3_image=Image.open(os.path.join(file_path,'right.png'))
                        st.image(c3_image,width=150,caption='right join')
                        st.markdown(""" 
                                    **Right Join**
      ecocash

                                    `Right Join` returns all records from the right table, and the matched records from the left table

                                      **Note:** The `RIGHT JOIN` keyword returns all records from the right table (table2), and the matching records from the left table (table1). The result is 0 records from the left side, if there is no match.
                                    """)
                    with c4:
                        #outer join
                        c4_image=Image.open(os.path.join(file_path,'outer.png'))
                        st.image(c4_image,width=150,caption='outer join')
                        st.markdown(""" 
                                    **Outer Join**

                                    `Outer Join` returns all records when there is a match in either left or right table 

                                    **Note:** The `OUTER JOIN`  keyword returns all records when there is a match in left (table1) or right (table2) table records.

                                    """)

                except Exception as e:
                    st.exception(e)

        if (uploaded_file is not None) and (uploaded_file_1 is not None):

                with st.spinner('Stage 1 of 2 Reading input files'):

                    x=0
                    df=pd.DataFrame()
                    st.header('Click the button below to run the report')
                    if st.button('Run Report',key=1):
                        my_bar = st.progress(0)
                        result=pd.merge(dataframe_finder(uploaded_file), dataframe_finder(uploaded_file_1), left_on=primary_left,right_on=primary_right, how=join_type,suffixes=("_1", "_2"))
                        my_bar.progress(40)
                        st.write(result)
                        df=result
                        x+=1
                        my_bar.progress(60)
                    if x!=0:
                        st.header('SAVE the report')
                        col6,col7,col8,col9 = st.columns((1,1,1,1))
                        remote_css('https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css')
                        with col6:
                            st.markdown(get_table_download_link(df,'csv',"Report as CSV"), unsafe_allow_html=True)

                        with col7:
                            st.markdown(get_table_download_link(df,'excel',"Report as Excel"), unsafe_allow_html=True)
                        my_bar.progress(100)
                        my_bar.empty()

    elif choice=='DUPLICATES REMOVER':
        st.title('DUPLICATES REMOVER')
        st.header('Identify and Remove Duplicate Records')
        st.markdown("""> At this section you can identify and remove dupicates based on single or multiple columns""")
        uploaded_file_3 = st.file_uploader("Upload your input here", type=["csv","xlsx","txt"])

        df = dataframe_finder(uploaded_file_3)
        duplicate =pd.DataFrame()
        if uploaded_file_3 is not None:
            #making use of a session to avoid page reload when input or menu is change
            #https://discuss.streamlit.io/t/multiselect-based-on-user-input/4188

            if 'key' not in st.session_state:
                st.session_state.columns_selected = False

            try:
                columns = df.columns.tolist()
                columns_selected = st.multiselect('Select columns : Note if you leave blank, it will search for duplicates based on all columns', columns)
                if columns_selected or st.session_state.columns_selected:
                    #this where the session is triggered
                    st.session_state.columns_selected = True
                    st.write(columns_selected)

                    #check if columns are selected
                    if columns_selected:
                        #duplicate = duplicate.append(df[df.duplicated(columns_selected)])
                        #in case we want to remove the original record from the files use that code as well
                        duplicate = df.loc[df.duplicated(subset=columns_selected, keep=False)]
                    else:
                        duplicate = duplicate.append(df[df.duplicated()])

                    if duplicate.empty:
                        st.warning('There are no duplicates found based on the matched criteria above')

                    else:
                        st.success("Duplicate files found")
                        st.subheader("Duplicate files found")
                        st.write(duplicate)

                        st.subheader("Handling File without Duplicates")
                        st.markdown("""> How do you want to handle the file without duplicates, Do you want to keep the first or last record of the duplicates in the new file or you want to remove all records that were not unique when you ran the report""")

                        dup_menu = ["KEEP FIRST RECORD OF THE DUPLICATE","KEEP LAST RECORD OF THE DUPLICATE","REMOVE ALL NON UNIQUE RECORDS "]

                        choice_dup_menu = st.selectbox("Menu",dup_menu)

                        if choice_dup_menu and (uploaded_file_3 is not None):
                            # dropping all duplicate values and keeping the first one only , it can be keep='last' or keep=False
                            try:
                                df.drop_duplicates(subset=columns_selected,keep =choice_download_dup(choice_dup_menu), inplace = True)
                                st.write(df)
                                st.subheader('Savings the report')
                                col6,col7,col8,col9 = st.columns((1,1,1,1))
                                remote_css('https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css')

                                with col6:
                                    st.markdown(get_table_download_link(duplicate,'csv',"Duplicates as CSV"), unsafe_allow_html=True)

                                with col7:
                                    st.markdown(get_table_download_link(duplicate,'excel',"Duplicates as Excel"), unsafe_allow_html=True)

                                with col8:
                                    st.markdown(get_table_download_link(df,'csv',"Unique Records as CSV"), unsafe_allow_html=True)

                                with col9:
                                    st.markdown(get_table_download_link(df,'excel',"Unique Records as Excel"), unsafe_allow_html=True)
                            except Exception as e:
                                st.error(e)

            except Exception:
                st.error('Failed to get the headers , the files is not formated correctly')


if __name__ == '__main__':
    main()
