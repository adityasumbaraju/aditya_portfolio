## Project 1: ETL Project: Data Preparation - Car sales' productivity


   <b> Data Preparation - ETL and Data Analysis Project </b> 
           <p>I have considered three datasets for the Data Preparation - ETL Project. The three datasets are linked based on the Make and Model of a given vehicle.<br />
 <b>Data source 1: flat file</b>
The CSV file containing the vehicle demographics, which is specific to the wheelbase, fuel type, and respective price of several motor vehicle models. Each row is one vehicle model, and each column is one specification such as engine size, fuel system, stroke, horsepower, highway mpg, city mpg, etc.<br />
 <img src="https://github.com/adityasumbaraju/aditya_portfolio/blob/main/Data_Preparation_Car_Sales_Productivity/images/DS1_stats.jpg" width="800"/><br />
 <img src="https://github.com/adityasumbaraju/aditya_portfolio/blob/main/Data_Preparation_Car_Sales_Productivity/images/DS1_corr.jpg" width="800"/>  <br />          
  </p> <br />
  <p>
 <b>Data Source 2: Website</b>
The Website that contains a table of the number of each vehicle model sold during 2020. Each row is one vehicle model. The website represents the make and model as car models. I split based on the pattern and assigned the values to respective columns to make the data more granular.<br />
 <img src="https://github.com/adityasumbaraju/aditya_portfolio/blob/main/Data_Preparation_Car_Sales_Productivity/images/DS2_stats.jpg" width="800"/>
 <img src="https://github.com/adityasumbaraju/aditya_portfolio/blob/main/Data_Preparation_Car_Sales_Productivity/images/DS2_corr.jpg" width="800"/>            
  </p> <br />

  <p>
 <b>Data Source 3: API</b>
I choose 2 API datasets to support my use case that contains the vehicle catalog and Vehicle mechanical demographics <br />
  <img src="https://github.com/adityasumbaraju/aditya_portfolio/blob/main/Data_Preparation_Car_Sales_Productivity/images/DS3_stats.jpg" width="800"/> <br />
 <img src="https://github.com/adityasumbaraju/aditya_portfolio/blob/main/Data_Preparation_Car_Sales_Productivity/images/DS3_corr.jpg" width="800"/> <br />           
  </p> <br />


 <p>
 <b>Transformation rules:</b> <br />
•	extract data from CSV files and perform data cleansing techniques.<br />
•	renamed few column names to make it more meaningful to understand and deduped the complete dataset.<br />
•	subjected the data set to pandas_profiling to identify the correlation between variables missing values and outliers in the dataset.<br />
•	Extract data from HTML sources and perform data parsing techniques using web scrapping python libraries<br />
•	import the HTML data and get it into a more readable format, such as a data frame using BeautifulSoup<br />
•	removed redundant data which is not required for my use case.<br />
•	converted the returned data into JSON format for ease of access.<br />
•	renamed and dropped a few of the columns which are not required for my use case.<br />
•	organized the retrieved data into a data frame.<br />
•	merged two API source data and created a cleansed dataframe with make and model as a grain of the data.<br />
    </p> <br />
    
 <p>
 <b>Visualizations </b> <br />
•	Scatter plot of horsepower (flat file) vs. Engine_Capacity (website)<br />
  <br />
   <img src="https://github.com/adityasumbaraju/aditya_portfolio/blob/main/Data_Preparation_Car_Sales_Productivity/images/viz_scatterplot.jpg" width="800"/><br />
 
•	Bar chart of average car Price (API) for each car make (flat file)<br />
  <br />
   <img src="https://github.com/adityasumbaraju/aditya_portfolio/blob/main/Data_Preparation_Car_Sales_Productivity/images/viz_boxplot.jpg" width="800"/><br />
 
•	Viewing the sales (website) for each make (flat file) as a pie chart<br />
  <br />
   <img src="https://github.com/adityasumbaraju/aditya_portfolio/blob/main/Data_Preparation_Car_Sales_Productivity/images/viz_piechart.jpg" width="800"/><br />
 

•	Density plot of duration_listed (flat file)<br />
  <br />
   <img src="https://github.com/adityasumbaraju/aditya_portfolio/blob/main/Data_Preparation_Car_Sales_Productivity/images/viz_densityplot.jpg" width="800"/><br />
 
• Boxplots of the Highway mpg distribution (flat file) for each car make (flat file)<br />
  <br />
   <img src="https://github.com/adityasumbaraju/aditya_portfolio/blob/main/Data_Preparation_Car_Sales_Productivity/images/viz_densityplot2.jpg" width="800"/><br />
 </p> <br />
 
 <p>
 <b>
Data Source References:</b> <br />
CSV: https://www.kaggle.com/ashydv/car-price-prediction?select=CarPrice_Assignment.csv
Website: https://www.carroya.com/buscar/vehiculos/t4e0.do
API: https://parseapi.back4app.com/classes/Carmodels_Car_Model_List?count=1&limit=100
Kaggle API: https://www.kaggle.com/lepchenkov/usedcarscatalog?select=cars.csv
 </p> <br />
