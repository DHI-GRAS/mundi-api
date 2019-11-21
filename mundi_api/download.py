import os
import shutil
import tempfile
from contextlib import closing
from multiprocessing.pool import ThreadPool
from pathlib import Path
from urllib.parse import urlparse
import requests
from tqdm import tqdm

PBAR = tqdm()


def download(url, outfile=None, workdir=None):
    """Downloads a file to the given location.
    This function stores unfinished downloads in the given working directory.

    Parameters
    ----------
    url:
        Mundi DIAS URL to download.
    outfile:
        Output filename or absolute path output file
    workdir:
        Path where incomplete downloads are stored.

    Returns
    -------
    None
    """
    filename = Path(urlparse(url).path).name
    outfile = _format_path(outfile)
    if os.path.isdir(outfile):
        outfile /= f'{filename}.zip'


    workdir = _format_path(workdir)

    temp = tempfile.NamedTemporaryFile(delete=False, dir=workdir)
    temp.close()
    local_path = temp.name

    _download_raw_data(url, local_path)
    shutil.move(local_path, outfile)


def download_from_s3(url, access_key, secret_key, target_path):
    from urllib.parse import urlparse
    import boto3
    from botocore.client import Config
    from mundi_api.mundi_storage import S3Storage

    s3_client = boto3.client(
        's3',
        endpoint_url='https://obs.eu-de.otc.t-systems.com/',
        use_ssl=False,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        config=Config(
            signature_version='s3',
            connect_timeout=60,
            read_timeout=60,
        )
    )
    path_split = urlparse(url).path.split('/')
    bucket = path_split[1]
    prefix = '/'.join(path_split[2:])
    product_folder = path_split[:-1]
    storage_client = S3Storage(s3_client)
    storage_client.download_product(bucket, prefix, os.path.join(target_path, product_folder))


def _format_path(path):
    if not path:
        path = Path(os.getcwd())
    else:
        path = Path(path)
    return path


def download_list(urls, outdir=None, workdir=None, threads=3):
    """Downloads a list of URLs

    Parameters
    ----------
    urls:
        Downloads a list of URLs.
    outdir:
        Output direcotry.
    workdir:
        Storage of temporary files.
    threads:
        Number of simultaneous downloads.
    Returns
    -------
    None
    """
    pool = ThreadPool(threads)
    download_lambda = lambda x: download(x, outfile=outdir, workdir=workdir)
    pool.map(download_lambda, urls)


def _download_raw_data(url, path):
    downloaded_bytes = 0
    with closing(
            requests.get(url, stream=True, timeout=10)
    ) as req, tqdm(
        unit='B',
        unit_scale=True
    ) as progress:
        chunk_size = 2 ** 20  # download in 1 MB chunks
        i = 0
        with open(path, 'wb') as openfile:
            for chunk in req.iter_content(chunk_size=chunk_size):
                if chunk:  # filter out keep-alive new chunks
                    openfile.write(chunk)
                    progress.update(len(chunk))
                    downloaded_bytes += len(chunk)
                    i += 1
        # Return the number of bytes downloaded
        return downloaded_bytes
