from json import load
from pandas.core.frame import DataFrame
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import time

from streamlit.type_util import Key

def count_time(func):
    def wrapper():
        timer = time.time()
        func()
        time_log = open("Exec_time_lab3.txt","a")
        time_log.write("\nFunction took: " + str(time.time() - timer) + " seconds")
        time_log.close()
    return wrapper

def get_Day_Of_Month(dt):
    return dt.day 
def get_Weekday(dt):
    return dt.weekday()
def get_Hours(dt):
    return dt.hour


@st.cache
def loadds1 ():
    ds1 = pd.read_csv("uber-raw-data-apr14.csv")
    ds1["Date/Time"] = pd.to_datetime(ds1["Date/Time"],format ="%m/%d/%Y %H:%M:%S")

    ds1.columns = ['Date/Time','lat','lon','Base'] 

    ds1["DoM"] = ds1["Date/Time"].map(get_Day_Of_Month)
    ds1["Weekday"] = ds1["Date/Time"].map(get_Weekday)
    ds1["Hours"] = ds1["Date/Time"].map(get_Hours)
    
    return ds1

@st.cache
def loadds2():
    ds2 =  pd.read_csv("ny-trips-data.csv")
    ds2["tpep_dropoff_datetime"] = pd.to_datetime(ds2["tpep_dropoff_datetime"],format ="%Y/%m/%d %H:%M:%S")
    ds2["tpep_pickup_datetime"] = pd.to_datetime(ds2["tpep_pickup_datetime"],format ="%Y/%m/%d %H:%M:%S")

    ds2["Vendor"] = ds2["VendorID"].apply(str)

    ds2["JourneyDuration"] =(ds2['tpep_dropoff_datetime']-ds2['tpep_pickup_datetime'])

    ds2["pickup_hours"] = ds2["tpep_pickup_datetime"].map(get_Hours)
    ds2["dropoff_hours"] = ds2["tpep_dropoff_datetime"].map(get_Hours)
   
    return ds2


def hist_pick_hour(ds,col):
    return np.histogram(
    ds[col], bins=24,range=(0.5,24))[0]
def hist_drop_hour(ds,col):
    return np.histogram(
    ds[col], bins=24,range=(0.5,24))[0]
def hist_dom(ds,col):
    return np.histogram(
    ds[col], bins=30,range=(0.5,30.5))[0]

def hist_week(ds,col):
    return np.histogram(
    ds[col], bins=7,range=(-.5,6.5))[0]

def hist_hour(ds,col):
    return np.histogram(
    ds[col], bins=24,range=(0.5,24))[0]

def count_Rows(df):
    return len(df)

def heat_map(ds,col1,col2):
            fig3, ax3 = plt.subplots(figsize=(4,3))
            color = sns.color_palette("magma", as_cmap=True)
            sns.plotting_context(font_scale=0.5)

            st.header("Heatmap of the busiest hours in a week")
            sns.heatmap(ds.groupby([col1, col2]).size().unstack(),ax=ax3, linewidths=.2, cmap="Reds")
            return fig3



#Choix du dataset et affichage
@count_time
def main():
    dataset_choice = option = st.sidebar.selectbox(
        'Which dataset do you want to study ?',
        ('Uber Trips in the NYC area in 2014','Taxi rides in the NYC area in 2015')
    )
    #dataset2
    if dataset_choice == 'Taxi rides in the NYC area in 2015':
        st.sidebar.write("You are looking at the second dataset")

        ds2 = loadds2()

        #st.write(ds2["JourneyDuration"])

        st.title("Taxi trips in a day in 2015")
        expander = st.expander("Original Dataset for the Taxi drivers")
        expander.write(ds2)


        st.header("Busiest pickup/dropoff Hours")
        option = st.selectbox(
        'What type of frequency do you want to see?',
        ('Busiest pickup hour', 'Busiest dropoff hour'))

        if option == "Busiest pickup hour":
            st.bar_chart(hist_pick_hour(ds2,"pickup_hours"))
        else:
            st.bar_chart(hist_drop_hour(ds2,"pickup_hours"))

        d1 = {'lat':ds2['pickup_latitude'],'lon':ds2['pickup_longitude']}
        d2 = {'lat':ds2['dropoff_latitude'],'lon':ds2['dropoff_longitude']}


        ds_pickup = pd.DataFrame(data = d1)
        ds_dropoff = pd.DataFrame(data = d2)

        st.header("Common pickup/dropoff points")
        choice = st.radio(
            "Choose between pickup or dropoff",
            ("common pickup points","common dropoff points")
        )


        if choice == 'common dropoff points':
            st.map(ds_dropoff)
        else:
            st.map(ds_pickup)

        st.header("Number of riders by driver")
        fig1, ax = plt.subplots(squeeze = True)
        ax.hist(ds2["Vendor"])
        ax.set_title("Number of riders by driver")
        st.pyplot(fig1)

    #dataset1
    else:
        st.sidebar.write("You are looking at the first dataset")
        st.title("Rideshare trips in 2014")

        ds1 = loadds1()
        
        expander = st.expander("Original Dataset for the Uber drivers")
        expander.write(ds1)


        option = st.selectbox(
            'What type of frequency do you want to see?',
            ('Day of the week', 'Day of the month', 'Hourly'))

        if option == "Day of the week":
            st.header("Number of riders by day in the week")
            st.bar_chart(hist_week(ds1,"Weekday"))
        elif option == "Day of the month":
            st.header("Number of riders by day in the month")
            st.bar_chart(hist_dom(ds1,"DoM"))
        else:
            st.header("Number of riders by hours")
            st.bar_chart(hist_hour(ds1,"Hours"))

        st.header("Frequent trips in NYC")
        hour = -1
        if st.checkbox('Do you want to see the position by hour ?'):
            hour = st.slider("Select the hour",0,23)
            i_map = ds1[ds1['Hours'] == hour]
            st.subheader(str(hour) + " h")
            st.map(i_map)
            
        else:
            hour = -1
            st.map(ds1)
        
        st.write(heat_map(ds1, 'Weekday', 'Hours'))

if __name__ == "__main__":
    main()
