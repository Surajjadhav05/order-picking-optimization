import pandas as pd
import streamlit as st 
from utils import prepare_data,perform_optimization

data_preparation=prepare_data()
optimization=perform_optimization()

st.title("Order Picking Optimization")
with st.expander("About the App"):
     st.write("""
         This web application help you to otpimize the product sequence of your online order based on the route, priority and route plus priority method.It will help you to optimize the pick up time simultaneously reduce product damage.
     """) 
st.sidebar.header("Welcome!")
file_type=st.sidebar.selectbox("Select File Type",("None","CSV","Excel"))
uploaded_file=st.sidebar.file_uploader("Please Share Order Details Here", type=["csv","excel"])
option=st.sidebar.selectbox("How would you like to optimize the order?",
                    ("None","Route Optimization","Priority Optimization","Route Plus Priority Optimization"))
@st.cache
def convert_df(df):
    return df.to_csv().encode('utf-8')
def give_download_option(df):
    file_optimized=convert_df(df)
    st.download_button("Download a Optimzed Product List",data=file_optimized, 
                   file_name="Optimized Product list.csv",mime="csv",key="Download csv")
    
def route_optimization(df):
    travel_subset=data_preparation.get_travel_subset_zones_route(df)
    tsp_routing=optimization.perform_tsp_routing(travel_subset[1])
    routeoptimized_zones=[]
    for i in tsp_routing:
         routeoptimized_zones.append(travel_subset[0][i])  
    df_route=pd.DataFrame()
    for i in routeoptimized_zones:
        d=df.loc[df.zone==i]
        df_route=pd.concat([df_route,d],ignore_index=True,axis=0).drop_duplicates(ignore_index=True)
        
    return df_route
      
if uploaded_file is not None:
    if file_type=="CSV":
        df=pd.read_csv(uploaded_file)
    else:
        df=pd.read_excel(uploaded_file)
        
    st.header("Order Details")
    st.dataframe(df)
    df=data_preparation.create_data(df)
    
    if option == "None":
        pass
    
    elif option =="Route Optimization":
        df_route=route_optimization(df)
        st.header("Route Optimized Order Details")
        df_route.drop(["zone","dept_priority"],axis=1,inplace=True)
        print(df_route)
        st.dataframe(df_route)
        give_download_option(df_route)
        
    elif option=="Priority Optimization":
        df=optimization.priority_optimization(df)
        df.drop(["zone","dept_priority"],axis=1,inplace=True)
        st.header("Priority Optimized Order Details")
        st.dataframe(df)
        give_download_option(df)
    
    elif option=="Route Plus Priority Optimization":
        if len(df.loc[df.dept_priority<7])<2:
            st.write("Route Plus Priority Optimization is not possible as low priority products are less in number")
        else:
            data=prepare_data.prepare_data_route_plus_priority(df)
            df_route=route_optimization(data[0])
            df_priority=optimization.priority_optimization(data[1])
            df_optimized=pd.concat([df_route,df_priority],axis=0).drop_duplicates(ignore_index=True)
            df_optimized.drop(["zone","dept_priority"],axis=1,inplace=True)
            st.header("Route plus Priority optimized Order Details")
            st.dataframe(df_optimized)
            give_download_option(df_optimized)
    else:
        pass
else:
    st.sidebar.write("Please Upload A Order Details and Select Optimization method")
        
        

            
