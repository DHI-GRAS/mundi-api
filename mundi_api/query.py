from urllib.parse import urlencode
import requests

from shapely.geometry import shape
from lxml import etree

from mundi_api._product_mappings import PRODUCT_MAPPINGS


QUERY_URL = ('https://catalog-browse.default.mundiwebservices.com'
             '/acdc/catalog/proxy/search/{satellite}/opensearch?productType={product}')


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
        query_params['timeStart'] = start_date.isoformat()
    if end_date is not None:
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


def query(satellite, product, start_date=None, end_date=None,
          geometry=None, progress_bar=True, **kwargs):
    """Query the mundi API for available products.

    Parameters
    ----------
    satellite: str
        Name of the satellite, e.g. Sentinel1, Sentinel2, Sentinel3.
    product: str
        Name of the product to query for, e.g. SLC, GRD, L1C, OLCI
    start_date: datetime.datetime
        Only find products on or after this date
    end_date: datetime.datetime
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
    products: list of dict
        List of found downloadable products. Each product contains the download link along with
        product-specific metadata. The included metadata depends on the mapping for the given
        product in _product_mappings.py. If no mapping is defined for the product, the default
        mapping is used.
    """
    query_str = _build_query(
        QUERY_URL.format(satellite=satellite, product=product),
        start_date,
        end_date,
        geometry,
        **kwargs
    )

    products = []
    pbar = None
    while query_str is not None:
        r = requests.get(query_str)
        r.raise_for_status()

        xml = etree.fromstring(r.content)

        query_str = _find_next(xml)

        mapping = PRODUCT_MAPPINGS.get(product, PRODUCT_MAPPINGS['default'])
        products += [_parse_entry(entry, mapping) for entry in
                     xml.findall('entry', namespaces=xml.nsmap) if _is_online(entry)]

        if progress_bar:
            if pbar is None:
                pbar = _get_pbar(xml)
            pbar.update()
            if query_str is None:
                pbar.close()

    return products
