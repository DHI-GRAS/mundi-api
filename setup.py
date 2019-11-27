from setuptools import setup, find_packages


setup(
    name='mundi_api',
    version='0.1',
    description='Query the Mundi OpenSearch API for available products',
    author='DHI GRAS',
    author_email='phgr@dhigroup.com',
    packages=find_packages(),
    python_requires='>=3.6',
    install_requires=[
        'requests',
        'shapely',
        'lxml',
        'tqdm',
        'python-dateutil'
    ],
    extras_require={
        's3': [
            'boto3'
        ]
    }
)
