import httpx
import pytest

TEST_ADDRESS = "http://127.0.0.1:8080"


def test_root():
    response = httpx.get(
        f"{TEST_ADDRESS}/"
    )
    assert response
    json_resp = response.json()
    assert json_resp
    return json_resp


@pytest.mark.parametrize(
    ["query", "must_haves"], (
    # ("",),
    ("pancake", {"pancakes",},),
    ("I like lemon juice and granuated sugar on my pancakes.", {"pancakes", "lemon juice"},),
))
def test_jobs(query, must_haves):
    response = httpx.post(
        f"{TEST_ADDRESS}/jobs",
        params=dict(
            text=query
        )
    )

    json_resp = response.text

    for must_have in must_haves:
        assert must_have in json_resp

    return json_resp
