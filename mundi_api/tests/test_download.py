from pathlib import Path
from urllib.parse import urlparse

from mundi_api.download import download, download_list


def test_download(url, tmp_path, workdir):
    create_workdir_if_not_exists(workdir)

    outfile = tmp_path
    download(url, outfile=outfile, workdir=workdir)
    write_path = list(outfile.glob("*"))[0]

    filename = Path(urlparse(url).path).name
    assert outfile / f'{filename}.zip' == Path(write_path)


def test_download_list(urls, tmp_path):
    outfile, workdir = tmp_path / "outfiles", tmp_path / "workdir"
    outfile.mkdir()
    workdir.mkdir()
    download_list(urls, outdir=outfile, workdir=workdir, threads=max(10,len(urls)))

    created_files = set()
    for p in outfile.glob("*"):
        created_files.add(str(p))
    file_assertions = set()
    for url in urls:
        filename = Path(urlparse(url).path).name
        file_assertions.add(str(outfile / f'{filename}.zip'))
    assert created_files == file_assertions


def create_workdir_if_not_exists(p):
    if p:
        print('THIS IS P ', p)
        p = Path(p)
        if not p.is_dir():
            p.mkdir()
