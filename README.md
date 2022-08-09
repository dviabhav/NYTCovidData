# Covid data visualization

I began writing the jupytr file during the first wave of covid to track covid cases as my wedding date drew closer. Using a personal python file allowed me to easily look at data from regions relevant to me. 
It grew into a larger project for me to learn how to use python script for data visualization and data scrapping.

<h2>Description</h2>
Much of the calculations and data handeling is done in the python script <i>data.py</i> which is imported to the juptyr script <i>Covid19 file.ipynb</i>.
 
 
Data is imported from various sources. 
<b>US Covid data, US state level data, and US County level data</b> is downloaded from NYTimes master data.

County population has been downloaded and saved as a csv file. County level data from NYTimes is mapped using fips, a column not available in county population file. I created Fips using columns available in county population.

The script calculates various entities such as weekly cases at the state and county level. Using population data it calculates cases/deaths per million.
Some calculations are legacy calculations that are irrelevant now. The partisan split in data was calculated during the tiem when there was a marked difference in Republican and Democratic governors response to the rising Covid cases.
