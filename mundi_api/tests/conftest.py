import os
import pytest
import uuid
from pathlib import Path

URL = 'https://obs.eu-de.otc.t-systems.com/s2-l1c-2019-q4/42/Q/UL/2019/10/24/S2B_MSIL1C_20191024T060919_N0208_R134_T42QUL_20191024T085607'
URLS = [URL] * 5


@pytest.fixture
def url():
    from random import choice
    return choice(URLS)


@pytest.fixture
def urls():
    return URLS


@pytest.fixture(params=[None, str(uuid.uuid1()), Path(str(uuid.uuid1()))])
def workdir(request):
    yield request.param

