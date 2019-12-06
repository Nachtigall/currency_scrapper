# Currency scrapper


## Create virualenv

First, create virtualenv if needed

```
virtualenv -p python3 ~/some/folder
```

Activate it

```
source ~/some/folder/bin/activate
```

## Install requirements

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install required libraries.

```
pip install -r /path/to/scrapper/requirements.txt
```

## Run scrapper
Navigate to the folder where you have downloaded currency scrapper.
```
python /path/to/scrapper/scrapper.py
```

## Results
Scrapper will download CSV file from [ecb website](https://www.ecb.europa.eu) with historical data.
In next step data will be extracted into two CSV files: 
- rates_by_dates.csv 
- rates_by_monthes.csv

Downloaded CSV file, as well as created CSV files with cleaned date, will be located in folder to which scrapper.py is downloaded.

## Future
No future work is planned.
