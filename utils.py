import pandas as pd
import numpy as np
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

travel_times = [
                [00.00, 15.58, 39.84, 49.84, 44.20, 40.67, 37.14, 40.67, 44.20, 47.73, 51.26, 70.33, 65.96, 74.83, 77.18],
                [15.58, 00.00, 24.26, 34.26, 28.62, 25.09, 21.56, 25.09, 28.62, 32.15, 35.68, 54.75, 50.39, 59.25, 61.60],
                [39.84, 24.26, 00.00, 24.06, 29.07, 31.76, 28.24, 31.76, 35.29, 38.82, 42.35, 61.42, 57.06, 65.92, 68.28],
                [49.84, 34.26, 24.06, 00.00, 21.91, 25.44, 28.97, 32.50, 36.02, 39.55, 43.08, 62.15, 57.79, 66.65, 69.01],
                [44.20, 28.62, 29.07, 21.91, 00.00, 16.47, 20.00, 23.53, 27.06, 30.59, 34.12, 53.18, 48.82, 57.69, 60.04],
                [40.67, 25.09, 31.76, 25.44, 16.47, 00.00, 16.47, 20.00, 23.53, 27.06, 30.59, 49.66, 45.29, 54.16, 56.51], 
                [37.14, 21.56, 28.24, 28.97, 20.00, 16.47, 00.00, 16.47, 20.00, 23.53, 27.06, 46.13, 41.76, 50.63, 52.98],
                [40.67, 25.09, 31.76, 32.50, 23.53, 20.00, 16.47, 00.00, 16.47, 20.00, 23.53, 29.66, 25.29, 34.16, 36.52],
                [44.20, 28.62, 35.29, 36.02, 27.06, 23.53, 20.00, 16.47, 00.00, 16.47, 20.00, 26.13, 21.76, 30.64, 32.99],
                [47.73, 32.15, 38.82, 39.55, 30.59, 27.06, 23.53, 20.00, 16.47, 00.00, 16.47, 22.60, 18.24, 27.11, 29.46],
                [51.26, 35.68, 42.35, 43.08, 34.12, 30.59, 27.06, 23.53, 20.00, 16.47, 00.00, 19.07, 14.71, 23.57, 25.92],
                [70.33, 54.75, 61.42, 62.15, 53.18, 49.66, 46.13, 29.66, 26.13, 22.60, 19.07, 00.00, 13.77, 22.64, 29.69],
                [65.96, 50.39, 57.06, 57.79, 48.82, 45.29, 41.76, 25.29, 21.76, 18.24, 14.71, 13.77, 00.00, 17.59, 14.26],
                [74.83, 59.25, 65.92, 66.65, 57.69, 54.16, 50.63, 34.16, 30.64, 27.11, 23.57, 22.64, 17.59, 00.00, 07.20],
                [77.18, 61.60, 68.28, 69.01, 60.04, 56.51, 52.98, 36.52, 32.99, 29.46, 25.92, 29.69, 14.26, 07.20, 00.00]
                ]

class prepare_data:
    def __init__(self):
        pass
    
    def create_data(self,df):
        zone={'frozen':13,'other':15,"bakery":4,'produce':11,'alcohol':14,'international':2,'beverages':14,'pets':8,'dry goods pasta':2,
        'bulk':9,'personal care':6,'meat seafood':12,'pantry':5,'breakfast':4,'canned goods':3,'dairy eggs':13,'household':10,
        'babies':7,'snacks':1,'deli':11,'missing':1}
        priority_dept={'frozen':12,'other':6,"bakery":13,'produce':14,'alcohol':10,'international':8,'beverages':9,'pets':2,'dry goods pasta':8,
        'bulk':1,'personal care':5,'meat seafood':12,'pantry':7,'breakfast':11,'canned goods':9,'dairy eggs':15,'household':3,
        'babies':4,'snacks':11,'deli':11,'missing':13}
        df['zone']=df['department'].map(zone)
        df["dept_priority"]=df["department"].map(priority_dept)
        return df
    
    def get_travel_subset_zones_route(self,df):
        unique_zones=df.zone.unique().tolist()
        if unique_zones.count(1)==0:
            unique_zones.insert(0,1)
        else:
            pass
        
        if unique_zones.count(15)==0:
            unique_zones.insert(len(unique_zones),15)
        else:
            pass
        
        travel_time_subset=[]
        for i in unique_zones:
            row=[]
            for j in unique_zones:
                row.append(travel_times[i-1][j-1])
            travel_time_subset.append(row)
        print(travel_time_subset)
    
        return unique_zones, travel_time_subset
    def prepare_data_route_plus_priority(self,df):
        df_route=df.loc[df.dept_priority<7]
        df_priority=df.loc[df.dept_priority>6]
        return df_route, df_priority
    
        
    

class perform_optimization:
    def __init__(self):
        pass
    
    def perform_tsp_routing(self,travel_time_subset):
        def create_data_model():
            data = {}
            data['distance_matrix'] =travel_time_subset
            data['num_vehicles'] = 1
            data['start'] = [0]
            data['end']=[len(travel_time_subset)-1]
            return data
        
        data=create_data_model()
        
        manager=pywrapcp.RoutingIndexManager(len(data["distance_matrix"]),data['num_vehicles'],data['start'],data['end'])
        routing=pywrapcp.RoutingModel(manager)
        def distance_callback(from_index, to_index):
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return data['distance_matrix'][from_node][to_node]
        
        transit_callback_index = routing.RegisterTransitCallback(distance_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
        
        dimension_name='Distance'
        routing.AddDimension(transit_callback_index,0,2000,True,dimension_name) 
        distance_dimension = routing.GetDimensionOrDie(dimension_name)
        
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
        
        def print_solution(manager,routing,solution):
            index=routing.Start(0)
            plan_output=[]
            route_distance=0
            while not routing.IsEnd(index):
                plan_output += [manager.IndexToNode(index)]
                previous_index = index
                index = solution.Value(routing.NextVar(index))
                route_distance += routing.GetArcCostForVehicle(previous_index, index, 0)
            plan_output += [manager.IndexToNode(index)]
            return(plan_output)
        solution = routing.SolveWithParameters(search_parameters)
        if solution:
            return print_solution(manager, routing, solution)
    
    
    def priority_optimization(self,df):
        df_product=pd.DataFrame()
        priority_dept=df.dept_priority.unique().tolist()
        priority_dept.sort()

        for idx in priority_dept:
            df_t=df.loc[df.dept_priority==idx]
            df_product=pd.concat([df_product,df_t],axis=0,ignore_index=True).drop_duplicates(ignore_index=True)
        return df_product
    