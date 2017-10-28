Welcome to the repository for my Udacity Machine Learning Nanodegree final project about electricity price forecasting. In this repo you will find all tools, datasets and documentation necessary to reproduce the results achieved in this project.

# Files
The main output of this project is a 25 pages report containing an in-depth explanation and description of the whole project development process and the final results. Refer to `Report.pdf` to view the whole report.

The final model developed in this project consists of three different code modules:
* `timeseries_model.ipynb`
* `multivariate_timeseries.ipynb`
* `renewables_model.ipynb`
* `linear_model.ipynb`
The first two modules produce interim results that are used as inputs for th `linear_model.ipynb` ('bottleneck features'). To follow along with the development process it is recommended to view the modules in the order above. Each module is also provided as an .html file.

The files
* `timeseries.py`
* `renewables.py`
contain additional functions that are used by the primary modules.

The script `grab_weather_data.py` can be used to obtain the original weather data used in this project. Running this script takes about 36 hours. Weather data is provided in a more convenient, preprocessed if you want to rerun the code in the modules that rely on this data. Please refer to the Datasets section of this readme.

The file `data_preprocessing.ipynb` contains the code used for preprocessing raw generation and load forecast data.

# Dependencies
Only the main dependencies are listed here. It is highly recommended to use an environment manager like anaconda to make sure all other dependencies are installed correctly.

* python 3.6
* keras 2.0.5 with tensorflow 1.1.0
* scikit-learn 0.19.0
* seaborn 0.7.1
* numpy, pandas, jupyter, matplotlib

If you want to follow along the preprocessing and visualization process of the raw weather data, you have to set up an own environment for that. Please note that these steps are optional and only necessary if you want to rerun the data procurement process on your own (which is not necessary). All primary modules operate without these dependencies. Following packages are required:
* python 2.7
* iris 1.13.0
* cartopy 0.15.0

To install iris, please refer to http://scitools.org.uk/iris/docs/latest/installing.html
Iris requires the external GRIP API to access .grib binary files. The documentation for that dependencies can be found under https://software.ecmwf.int/wiki/display/GRIB/Home . Warning: Installing the grib api can be a real pain. I tried several tutorials and recommendations. The one that finally solved the installation problems can be found under https://ubuntuforums.org/showthread.php?t=2060457 

# Datasets
All necessary datasets are provided within this repository, except for the weather used as an input for one module. The full formatted weather dataset has a size of 10GB. It is provided under the following link:

If you want to rerun parts of the code that rely on that dataset, please download this file and unpack all data to /processed_data/weather

The data is stored in numpy binary objects. To aquire the acutal raw data from the original source, please refer to the script `grab_weather_data.py`.

All other data is stored in the /raw_data and /processed_data directories.
