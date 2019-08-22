#Import Flask packages
from flask import Flask
from flask import send_file, render_template

#Create app
app = Flask(__name__)


#Import other python packages
import pandas as pd
from bs4 import BeautifulSoup
import requests
import matplotlib.pyplot as plt
import numpy as np

def get_tables(url): 
    '''
    Objective: To find all of the relevant tables in a given url
    
    Input: url(string) - The url of the desired website
    
    Output: tables(list) - All of the tables that can be found in the url'''
    
    try: 
        #Get the response then request all tables
        response = requests.get(url, timeout = 5)
        content = BeautifulSoup(response.content, "html.parser")
        tables = content.find_all('table')
        
    except Exception as e: 
        #There would either be an error with finding tables or URL being unreachable
        print('Something went wrong, check your url')
        tables= ['Try Again!']
    
    return tables


def parse_table(table):
    '''
    Objective: Given a table, create a pandas df of the relevant information in the correct format
    
    Input: Table (HTML string) 
    
    Output: df (pandas df)
    
    '''
    
    rows = table.find_all('tr')
    
    #Empty list for our column names
    cols = []
    
    #Empty list for our column values
    vals = []
    
    #Tables will typically either have th (header values) or td (data values)
    #Lets make sure we categorize headers correctly 
    for row in rows: 
        
        headers = row.find_all('th')
        
        if len(headers) > 0:
            #If there's only one header, that will typically mean that this row is a title of the table
            if len(headers) == 1: 
                print('Table name: ', headers[0].get_text())
            
            else:
                #If there are a bunch of headers, they will be column names 
                for head in headers: 
                    cols.append(head.get_text())
                    
        else: 
            #If there are no headers, it should be data values
            data = row.find_all('td')
            
            #If the len of the data matches that of the columns, we want to add it in
            if len(data) == len(cols):
                
                #Create empty list for an entire row of observations
                one_row = []
                
                for obs in data: 
                    one_row.append(obs.get_text())

                vals.append(one_row)
            
            else: 
                continue
        
    df = pd.DataFrame(vals, columns = cols)
 
    return df


def cleanse_percents(df): 
    
    '''
    Objective: For columns that are strings and contain percents, we will make them numeric
    
    Input: df (pandas df) - unprocessed df with some strings
    
    Output: df (pandas df) - processed df with all numeric values
    '''
    #Get columns
    cols = df.columns
    
    for col in cols: 
        #If its already numeric, dont bother
        if (df[col].dtype == np.float64) | (df[col].dtype == np.int64): 
            continue
            
        else:
            #If it has a percent, change it to numeric, otherwise dont touch it
            if any("%" in val for val in df[col].values): 
                df[col] = df[col].apply(lambda x: float(x[:-1]))

            else: 
                df[col] = pd.to_numeric(df[col], errors = 'coerce')
            
    return df
            





@app.route('/')
def hello():
    
    #Get Tables
    tables = get_tables('https://www.macrotrends.net/2015/fed-funds-rate-historical-chart')
    #Im cheating and I know the first one is going to be the rates
    table = tables[0]
    #Parse it
    df = parse_table(table)
    #Make it numeric
    df = cleanse_percents(df)
    
    #Create a visualization
    plt.figure(figsize = (8,6))

    #Visualize
    plt.plot(df['Year'], df['Average Yield'])
    plt.ylabel('Average Yield %')
    plt.xlabel('Year')
    plt.title('Average Bond Yield')
    
    #Save into static files
    plt.savefig('static/Yield.png')
    filename = 'static/Yield.png'
   
    
    #Return the HTML endpoint with the file we want
    return render_template("sample.html", user_image = filename)



if __name__ == '__main__':
    app.run()