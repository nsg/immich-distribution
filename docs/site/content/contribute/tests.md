+++
title = "Tests"
+++

# Tests

The tests are triggered as part of a GitHub Action in any Pull Request you open.

## Run the tests locally

Install the snap locally, then run the snap tests from the repository root:

```
uv run --project tests pytest -s -v --run-snap-tests tests
```

## HAProxy test

`tests/test_haproxy.py` queries the HAProxy stats endpoint and fails if any backend is DOWN. It usually takes around a minute or two after installation for the state to get ready, so the test waits for the server to respond before checking the backends.

The HAProxy tests are configured like this:

```
backend be_server
    option httpchk
    http-check send meth GET uri /server-info/ping
    server immich-server 127.0.0.1:3001 maxconn 64 check inter 5s fall 2 rise 6
```

To summarize, HAProxy does a few basic backend checks to make sure that the services run correctly. I use this information to detect if everything is started and behaves correctly. This is exposed with the `tests/test_haproxy.py` test.

## Asset processing tests

The asset processing tests use API calls against a running Immich Distribution instance and are split into separate files so CI can run them independently:

1. `tests/test_assets_uploads.py` uploads all assets in `tests/assets` and selected upstream test assets, waits for processing, and verifies the asset count.
2. `tests/test_assets_exif.py` uploads the EXIF fixtures and verifies video/image type, location extraction, and image metadata.
3. `tests/test_assets_people.py` uploads the people fixtures, triggers face detection, and verifies that people are detected.
4. `tests/test_assets_ocr.py` uploads the OCR fixture and verifies extracted text and response structure.

I hope to add more tests over time, like more filetypes. If you like to contribute a file with an appropriate license, open an issue.
