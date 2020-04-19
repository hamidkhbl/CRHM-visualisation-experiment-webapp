## The Cold Regions Hydrological Model (CRHM) data visualization

### Environment set up
> Clone the repository and use the following command to install the required packages.
>
> `pip install -U -r requirements.txt`

### Plot an observation file
> `python plot.py <obs_file>`
>
> this code will plot your observation file on a html file.

### Plot two observation files for comparison
> `python compare.py <obs_file1> <obs_file2> <base>`
> 
>base = 'time' or 'id'
> Comparison is based on either time or id. Comparison based on time considers time as a base for comparison. However, comparison based on id will match data based on their appearance. Using id as the base may cause more mismatches if the start time for files is different.