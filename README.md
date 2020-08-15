** project in progress **

# Life Log Project
Originally the aim of this project was directed at understanding how much of my time I was putting into my primary job as well as the startup I was working with remotely, in an attempt to better manage my time, but it turned into something wholely different. The quantified self community also referrs to this type of thing as a data journal. 

Since I started manually recording in my lifelog in 2018 the category model has changed every year, usually to include more categories but more importantly to allow for more granularity in those aspects of my life that I'm interested in observing from a different perspective. For the purposes of this analysis I've consolidated categories from each year down to 5 categories: daily, exercise, social, wasted time, and work.

## Lifelog
Example of 2020 logging sheet
![log_screen_shot](https://github.com/william-cass-wright/quantified_self_life_log/blob/master/images/log_screen_shot.png)

## Analyses
### PCA & K-Means Clustering EDA
K-means clustering on dimensionally reduced daily sums
![kmeans](https://github.com/william-cass-wright/quantified_self_life_log/blob/master/images/kmeans.gif)  
Tableau Dashboard
![tableau_snap_shot](https://github.com/william-cass-wright/quantified_self_life_log/blob/master/images/tableau_snap_shot.png)
### Calendar plots
Daily
![daily](https://github.com/william-cass-wright/quantified_self_life_log/blob/master/images/2020-08-06_category_calplot_Daily.png)
Exercise
![exercise](https://github.com/william-cass-wright/quantified_self_life_log/blob/master/images/2020-08-06_category_calplot_Exercise.png)
Social
![social](https://github.com/william-cass-wright/quantified_self_life_log/blob/master/images/2020-08-06_category_calplot_Social.png)
Wasted Time
![wasted_time](https://github.com/william-cass-wright/quantified_self_life_log/blob/master/images/2020-08-06_category_calplot_Wasted_Time.png)
Work
![work](https://github.com/william-cass-wright/quantified_self_life_log/blob/master/images/2020-08-06_category_calplot_Work.png)
### To Do
- continute to refine function, class, and module structure
- bash scripts: run.sh and test.sh with sys inputs

## Other Analyses
- Cov-SARS-2 impact on daily/weekly behavior
- model-free analyses such as dynamic time warping, shapelets, or principal component analysis
- spectral analysis or clustering
- Utility: While there are many analyses that are good at processing multidimensional time series data I find that the more interesting analysis for me is a model specific to the data. Utility metrics, by my definition, are those that give usage of a service over a resource such as money or time. In my case I happen to have a detailed record of all my recurring spends that can give a monetary utilization of subscription services that are recorded in my life log. 

## Enhancments
- bring in other data sets such as PersonalCapital, RescueTime, or Google data