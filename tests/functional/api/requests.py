import httpx
import pytest

TEST_ADDRESS = "http://127.0.0.1:8000"


def test_root():
    response = httpx.get(
        f"{TEST_ADDRESS}/"
    )
    json_resp = response.json()
    print(json_resp)
    return json_resp


@pytest.mark.parametrize(
    ["query"], (
    # ("",),
    ("pancake",),
))
def test_jobs(query):
    response = httpx.post(
        f"{TEST_ADDRESS}/jobs",
        params=dict(
            q=""
        )
    )
    json_resp = response.text
    print(json_resp)
    return json_resp

