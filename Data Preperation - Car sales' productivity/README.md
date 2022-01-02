## Data Preparation - ETL and Data Analysis Project

I have considered three datasets for the Data Preparation - ETL Project. 
The three datasets are linked based on the Make and Model of a given vehicle.  

# Data source 1: flat file. 
The CSV file containing the vehicle demographics, which is specific to the wheelbase, fuel type, and respective price of several motor vehicle models. 
Each row is one vehicle model, and each column is one specification such as engine size, fuel system, stroke, horsepower, highway mpg, city mpg, etc.

# Data Source 2: Website
The Website that contains a table of the number of each vehicle model sold during 2020. Each row is one vehicle model.
The website represents the make and model as car models. I split based on the pattern and assigned the values to respective columns to make the data more granular.

# Data Source 3: API 
I choose 2 API datasets to support my use case that contains the vehicle catalog and Vehicle mechanical demographics

# Transformation rules:
1.  extract data from CSV files and perform data cleansing techniques. 
2.	renamed few column names to make it more meaningful to understand and deduped the complete dataset.
3.	subjected the data set to pandas_profiling to identify the correlation between variables missing values and outliers in the dataset.
4.	Extract data from HTML sources and perform data parsing techniques using web scrapping python libraries
5.	import the HTML data and get it into a more readable format, such as a data frame using BeautifulSoup
6.	removed redundant data which is not required for my use case.
7.	converted the returned data into JSON format for ease of access.
2.	renamed and dropped a few of the columns which are not required for my use case.
3.	organized the retrieved data into a data frame.
4.	merged two API source data and created a cleansed dataframe with make and model as a grain of the data.



# visualizations
•	Scatter plot of horsepower (flat file) vs. Engine_Capacity (website)

•	Bar chart of average car Price (API) for each car make (flat file)

•	Viewing the sales (website) for each make (flat file) as a pie chart

•	viewing Histogram of 'engine_fuel (API) vs. city mpg (flat-file)

•	Density plot of duration_listed (flat file)

•	Boxplots of the Highway mpg distribution (flat file) for each car make (flat file)


# Data Source References:
CSV: https://www.kaggle.com/ashydv/car-price-prediction?select=CarPrice_Assignment.csv

Website: https://www.carroya.com/buscar/vehiculos/t4e0.do

API: https://parseapi.back4app.com/classes/Carmodels_Car_Model_List?count=1&limit=100

Kaggle API: https://www.kaggle.com/lepchenkov/usedcarscatalog?select=cars.csv
