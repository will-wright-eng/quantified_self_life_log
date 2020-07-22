** project in progress **

# Life Log Project
Originally the aim of this project was directed at understanding how much of my time I was putting into my primary job as well as the startup I was working with remotely, in an attempt to better manage my time, but it turned into something wholely different. The quantified self community also referrs to this type of thing as a data journal. 

Since I started my life log in 2018 the category model has changed every year, usually to include more categories but more importantly to allow for more granularity in those aspects of my life that I'm interested in observing from a different perspective.

## Utility
While there are many analyses that are good at processing multidimensional time series data I find that the more interesting analysis for me is a model specific to the data. Utility metrics, by my definition, are those that give usage of a service over a resource such as money or time. In my case I happen to have a detailed record of all my recurring spends that can give a monetary utilization of subscription services that are recorded in my life log. 

### Summary
- recurring spend
- life log tables

### Requirements
- config_google
- config_lifelog
- config_recurringspend

### To Do
- convert lifelog class file to module 
- create app script as top-level of abstraction
- create spend_utilization module

### Utility Analysis
Calendar plot example: sleep per day
![sleep](https://github.com/william-cass-wright/quantified_self_life_log/blob/master/images/Sleep.png)
Tableau dashboard showing time series of spend categories

## Other Analyses
- Cov-SARS-2 impact on daily/weekly behavior
- model-free analyses such as dynamic time warping, shapelets, or principal component analysis
- spectral analysis or clustering

## Enhancments
- bring in other data sets such as PersonalCapital, RescueTime, or Google data