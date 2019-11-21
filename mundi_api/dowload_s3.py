def donwload_from_s3(url, access_key, secret_key, target_path):
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
    storage_client = S3Storage(s3_client)
    storage_client.download_product(bucket, prefix, target_path)
