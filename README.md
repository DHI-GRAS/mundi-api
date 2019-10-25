# Mundi-api
Query the [Mundi OpenSearch API](https://mundiwebservices.com/help/documentation) for available products.

## Usage
Exposes a single function `query`

```python
from mundi_api.query import query
from mundi_api.download import download, download_list
import geojson


from datetime import datetime

with open('my_shape.geojson') as f:
    my_shape = geojson.load(f)

q = query('Sentinel1', 'SLC',
      start_date=datetime(2019, 1, 1),
      end_date=datetime(2019, 1, 2),
      geometry=my_shape)

download_links = [q[sat_id]['link']['href'] for sat_id in q.keys()]

download(download_links[0], outfile='/home/andreas/data/')

download_list(download_links[1:11], threads=10)
```

```python
[
    ...,
    {'link': 'https://obs.eu-de.otc.t-systems.com/s1-l1-slc-2019-q1/2019/01/02/IW/DV/S1B_IW_SLC__1SDV_20190102T004408_20190102T004435_014308_01A9F3_A75C.zip',
    'title': 'S1B_IW_SLC__1SDV_20190102T004408_20190102T004435_014308_01A9F3_A75C',
    'orbit_direction': 'ASCENDING',
    'relative_orbit': '107',
    'polarisation': 'VV/VH',
    'sensing_date': '2019-01-02T00:44:08Z'},
    {'link': 'https://obs.eu-de.otc.t-systems.com/s1-l1-slc-2019-q1/2019/01/02/IW/DV/S1B_IW_SLC__1SDV_20190102T004432_20190102T004500_014308_01A9F3_F90E.zip',
    'title': 'S1B_IW_SLC__1SDV_20190102T004432_20190102T004500_014308_01A9F3_F90E',
    'orbit_direction': 'ASCENDING',
    'relative_orbit': '107',
    'polarisation': 'VV/VH',
    'sensing_date': '2019-01-02T00:44:32Z'},
    {'link': 'https://obs.eu-de.otc.t-systems.com/s1-l1-slc-2019-q1/2019/01/02/IW/DV/S1B_IW_SLC__1SDV_20190102T004458_20190102T004521_014308_01A9F3_7277.zip',
    'title': 'S1B_IW_SLC__1SDV_20190102T004458_20190102T004521_014308_01A9F3_7277',
    'orbit_direction': 'ASCENDING',
    'relative_orbit': '107',
    'polarisation': 'VV/VH',
    'sensing_date': '2019-01-02T00:44:58Z'},
    ...
]
```
