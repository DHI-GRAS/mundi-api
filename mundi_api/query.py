import datetime
from urllib.parse import urlencode
import dateutil.parser
import requests

from shapely.geometry import shape
from lxml import etree

from mundi_api._product_mappings import PRODUCT_MAPPINGS


QUERY_URL = ('https://catalog-browse.default.mundiwebservices.com'
             '/acdc/catalog/proxy/search/{satellite}/opensearch?maxRecords=50')


def _parse_date(date):
    if isinstance(date, datetime.datetime):
        return date.replace(microsecond=0)
    try:
        return dateutil.parser.parse(date).replace(microsecond=0)
    except ValueError:
        raise ValueError('Date {date} is not in a valid format. Use Datetime object or iso string')


def _add_time(date):
    if date.hour == 0 and date.minute == 0 and date.second == 0:
        date = date + datetime.timedelta(hours=23, minutes=59, seconds=59)
        return date
    return date


def _recursive_dict(element):
    import re
    if not element.text and len(element.attrib):
        return re.sub(r"\s*{.*}\s*", "", element.tag), element.attrib
    return re.sub(r"\s*{.*}\s*", "", element.tag), \
        dict(map(_recursive_dict, element)) or element.text


def _tastes_like_wkt_polygon(geom):
    try:
        return geom.strip().startswith('POLYGON (')
    except AttributeError:
        return False


def _parse_geometry(geom):
    try:
        # If geom has a __geo_interface__
        return shape(geom).wkt
    except AttributeError:
        if _tastes_like_wkt_polygon(geom):
            return geom
        raise ValueError('geometry must be a WKT polygon str or have a __geo_interface__')


def _build_query(base_url, start_date=None, end_date=None, geometry=None, **kwargs):
    query_params = {}

    if start_date is not None:
        start_date = _parse_date(start_date)
        query_params['timeStart'] = start_date.isoformat()
    if end_date is not None:
        end_date = _parse_date(end_date)
        end_date = _add_time(end_date)
        query_params['timeEnd'] = end_date.isoformat()

    if geometry is not None:
        query_params['geometry'] = _parse_geometry(geometry)

    # Add or potentially overwrite query params with custom user params
    query_params.update(kwargs)

    if query_params:
        base_url += f'&{urlencode(query_params)}'

    return base_url


def _find_next(xml):
    next_link = None
    for link in xml.findall('link', namespaces=xml.nsmap):
        if link.attrib['rel'] != 'next':
            continue
        next_link = link.attrib['href']
    return next_link


def _find_dl_link(xml):
    dl_link = None
    for link in xml.findall('link', namespaces=xml.nsmap):
        if link.attrib['rel'] != 'enclosure':
            continue
        dl_link = link.attrib['href']
    return dl_link


def _is_online(xml):
    return xml.findtext('DIAS:onlineStatus', namespaces=xml.nsmap) == 'ONLINE'


def _parse_entry(xml, mapping):
    product = {}
    product['link'] = _find_dl_link(xml)

    for xml_name, prod_name in mapping:
        product[prod_name] = xml.findtext(xml_name, namespaces=xml.nsmap)

    return product


def _get_pbar(xml):
    import tqdm

    total = int(xml.findtext('os:totalResults', namespaces=xml.nsmap))
    per_page = int(xml.findtext('os:itemsPerPage', namespaces=xml.nsmap))

    return tqdm.tqdm(total=total // per_page + 1)


def query(satellite, start_date=None, end_date=None,
          geometry=None, progress_bar=True, **kwargs):
    """Query the mundi API for available products.

    Parameters
    ----------
    satellite: str
        Name of the satellite, e.g. Sentinel1, Sentinel2, Sentinel3.
    product: str
        Name of the product to query for, e.g. SLC, GRD, L1C, OLCI
    start_date: datetime.datetime, str
        Only find products on or after this date
    end_date: datetime.datetime, str
        Only find products on or before this date
    geometry: WKT polygon or object implementing __geo_interface__
        Geometry of area to search within
    progress_bar: bool
        Show a progress bar during query.
        Requires tqdm.
    kwargs:
        Any kwargs will be passed as query parameters to the query,
        potentially also overriding satellite, product, dates or geometry

    Returns
    -------
    dict[string, dict]
        Products returned by the query as a dictionary with the product ID as the key and
        the product's attributes (a dictionary) as the value.
    """
    query_str = _build_query(
        QUERY_URL.format(satellite=satellite),
        start_date,
        end_date,
        geometry,
        **kwargs
    )

    products = {}
    pbar = None
    while query_str is not None:
        r = requests.get(query_str)
        r.raise_for_status()

        xml = etree.fromstring(r.content)

        query_str = _find_next(xml)

        for entry in xml.findall('entry', namespaces=xml.nsmap):
            if _is_online(entry):
                entry_dict = _recursive_dict(entry)[1]
                products[entry_dict['id']] = entry_dict
        if progress_bar:
            if pbar is None:
                pbar = _get_pbar(xml)
            pbar.update()
            if query_str is None:
                pbar.close()

    return products
