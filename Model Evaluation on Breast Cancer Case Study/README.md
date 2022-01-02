## Breast Cancer Prediction - Model evaluation

Essentially, data mining is the act of discovering innovative data models that are possibly helpful, valid, and finally comprehensible. An enormous quantity of medical data is being generated due to medical database management technologies and methods that are cutting-edge (Bakr et al.,2020). Breast cancer research data will be analyzed utilizing supervised learning techniques. A breast cancer dataset is analyzed using bioinformatics classification techniques.
The first data set is classified using an optimal algorithm for the detection and prediction of breast cancer. The proposal enables us to choose the most effective classification for breast cancer prediction, assess different approaches for mining data from the breast cancer dataset, and determine the most successful performance-based strategy for disease prediction.
Doctors and healthcare researchers may better understand their patients via text and visual data analysis using medical data analysis. In this project, I will be exploring the feature reduction properties of independent component analysis on the breast cancer prediction model. The actual data with 30 features and reduced one feature is used to evaluate the accuracy of the classifiers such as support vector machine (SVM), k-nearest neighbor (k-NN), and logistic regression. These classifiers are evaluated in terms of specificity, sensitivity, accuracy, F-score that helps to categorize tumors as benign and malignant. The result will be a comparison of the proposed classification using the initial feature set is also tested on different validation using 10-fold cross-validations and partitioning (20%–40%) methods. 

# Problem Statement
Breast cancer is diagnosed in a large number of persons each year. A challenging diagnosis is required since the illness has a human origin. As a consequence of these and other incidents, the use of machine learning and computers to detect this disease has risen significantly in recent years. We evaluate several classification learning algorithms to prevent benign and malignant cancers based on a breast cancer dataset. I will be focusing on machine learning algorithms that I have learned throughout this course. 

# Metadata
Dataset classifies the Benign and Malignant cells using the description of the cells in the form of columnar attributes. This data was donated by researchers of the University of Wisconsin and included the measurements from digitized images of fine-needle aspirate of a breast mass.
The data sets are provided with 569 examples of cancer biopsies, each with 32 features. One feature is an identification number, another is the cancer diagnosis, and 30 are numeric-valued laboratory measurements. 
The diagnosis is coded as 

1. "M" to indicate malignant.

2. "B" to distinguish benign.

The other 30 numeric measurements comprise the mean, standard error, and worst (i.e., most significant) value for ten different characteristics of the digitized cell nuclei.

# Exploratory Data Analysis
By using exploratory data analysis, physicians may more accurately predict whether or not a patient's cancer will return and how long they will survive (EDA). Python is used in EDA research to analyze and compute statistics and graphically display the results. Since the Dataset is derived from actual patient records of breast cancer patients, missing values cannot be imputed. 
I have used descriptive statistics to derive mean, SD, and correlation. After grouping on diagnosis, it has been observed that 357 observations indicate the absence of cancer cells and 212 show absence of cancer cell

# Model Comparision
Model	          SVM	  LogisticRegression	  RandomForest	  KNN
Prediction Yes	82	  80	                  77	             81
Prediction -No	146	  148	                  151	             147
Accuracy	      97%	  98%	                  97%	             98%

Compared to logistic regression, Random Forest, KNN, and SVM, the logistic regression model was more accurate in predicting breast cancer's class. It seems that for the classification of breast cancer class, the logistic regression method is appropriate. The Logistic regression correctly classifies patients with and without breast cancer 96% of the time. Its AUC of 99% indicates a remarkable ability to distinguish between a benign lump and a malignant tumor
In the Anaconda environment, all algorithms have been programmed in Python using the scikit-learn library. After an accurate comparison between our models, I found that the logistic regression achieved a higher efficiency of  98%, Precision of 97.5%, AUC of 99 %, and outperformed all other algorithms. In conclusion, Logistic regression has demonstrated its efficiency in Breast Cancer prediction and diagnosis and achieves the best performance in terms of accuracy and Precision. 

# References

Wolberg WH, Street WN, Heisey DM, Mangasarian OL. Computerized breast cancer diagnosis and prognosis from fine-needle aspirates. Arch Surg. 1995 May;130(5):511-6. doi: 10.1001/archsurg.1995.01430050061010. PMID: 7748089.

Bakr, M. A. H. A., Al-Attar, H. M., Mahra, N. K., & Abu-Naser, S. S. (2020). Breast Cancer Prediction using JNN. International Journal of Academic Information Systems Research (IJAISR), 4(10).
Dhahri, H., Al Maghayreh, E., Mahmood, A., Elkilani, W., & Faisal Nagi, M. (2019). Automated breast cancer diagnosis based on machine learning algorithms. Journal of healthcare engineering, 2019.
Islam, M. M., Haque, M. R., Iqbal, H., Hasan, M. M., Hasan, M., & Kabir, M. N. (2020). Breast cancer prediction: a comparative study using machine learning techniques. SN Computer Science, 1(5), 1-14.
Khourdifi, Y., & Bahaj, M. (2018, December). Applying best machine learning algorithms for breast cancer prediction and classification. In 2018 International conference on electronics, control, optimization and computer science (ICECOCS) (pp. 1-5). IEEE.

Dataset:
http://archive.ics.uci.edu/ml/datasets/breast+cancer+wisconsin+%28diagnostic%29
 Dua, D. and Graff, C. (2019). UCI Machine Learning Repository [http://archive.ics.uci.edu/ml]. Irvine, CA: University of California, School of Information and Computer Science. 

