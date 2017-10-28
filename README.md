# DA-electricity-price-forecasting
Forecasting Day-Ahead electricity prices in the German bidding zone with deep neural networks.

Welcome to the repository for the Udacity Machine Learning Nanodegree final project about electricity price forecasting. In this repo you will find all tools, datasets and documentation necessary to reproduce the results achieved in this project.

## Datasets
All necessary datasets are provided within this repository, except for the weather used as an input for one module. The full formatted weather dataset has a size of 10GB. It is provided under the following link:

If you want to rerun parts of the code that rely on that dataset, please download this file and unpack all data into the repository /processed_data/weather

The data is stored in a numpy binary object. To aquire the acutal raw data from the original source, please refer to the script `grab_weather_data.py`.
