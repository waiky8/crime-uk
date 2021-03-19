# Crime UK
This is a simple crime dashboard that show all reported crimes at local area level. Local area is defined as Middle Layer Super Output Areas (MSOA) that is commonly used in the UK to improve reporting of small areas. Built on **Dash** and written in **Python**, the data is sourced from PoliceUK site https://data.police.uk/data/.<br><br>

**Mapbox** is used to show the crime locations that dispalys additional information when you hover over or click on the markers.<br><br>

Data is refreshed monthly. Note that due to the size of the files it is only possible to hold one month's worth of data.<br><br>
The application is uploaded to **Heroku**.<br><br>
Check it out at https://crime-uk.herokuapp.com/<br><br>

# Features:
- Summary of crime by crime type
- Datatable with additional information, including the outcome of investigations
- Map with markers showing the locations where the crime occurred
- More serious crimes are coloured red / orangered
- Compare crimes by entering multiple areas
- Postcode lookup to assist in determining the correct local area name - achieved by web scraping https://www.doogal.co.uk/ using **beautifulsoup4**

# Input options:
- Select local area(s)
- Select crime type(s)

# Description of code/files:
 - **app.py** - main application code
 - **app_msoa.py** - code to add local area name (MSOA) column to input files
 - **app_colour.py** - code to add colour column to input files (used for marker colours on the map)
 - **2021-01-xxx-street.csv** - crime files by constabulary

Note some data files not uploaded due to github storage limitation.

# Sample screenshots:
![alt text](https://github.com/waiky8/crime-uk/blob/main/screenshot_1.jpg)
![alt text](https://github.com/waiky8/crime-uk/blob/main/screenshot_2.jpg)
![alt text](https://github.com/waiky8/crime-uk/blob/main/screenshot_3.jpg)
