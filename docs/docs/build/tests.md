# Tests

The rests are triggered as part of an GitHub Action in any Pull Request you open.

## Run the tests locally

In the `tests/` folder, run `make selenium` to start a selenium container in podman. In another terminal run `make test` to fire up the tests.

## HAProxy test

`test_haproxy.sh` queries the HAProxy stats endpoint, it will fail if there is any DOWN backens. I use this like below to wait for the different components to start. It usually takes around a minute or two for the state to get ready.

```makefile
wait:
	while ! ./test_haproxy.sh ; do sleep 1; done
```

The HAProxy tests are configured like this:

```
backend be_microservices
    {==option httpchk==}
    {==http-check send meth GET uri /ping==}
    server microservices 127.0.0.1:3003 maxconn 32 {==check==} inter 10s fall 2 rise 6
```

To summarize, HAProxy do a few basic backend checks to make sure that the services runs correctly. I use this information to detect if everyting is started and behaves correctly. This is exposed with the `test_haproxy.sh` script.

## Selenium tests

These tests are triggered when the above tests succeeds. If you have started the selenium container, you can inspect the selenium browser process at [localhost:7900](http://localhost:7900) (password: `secret`).

The selenium tests are inside `tests_selenium.py`. The tests is a mix of browser tests, API calls and cli commands. At the moment the test contains these steps:

1. Register a user
2. Log in with the above user and check for JS and 404 errors
3. Make sure that we have an empty timeline
4. Make an API key
5. Verify that we can execute the CLI
6. Upload all assets in `tests/assets` to Immich via the CLI using the API key
7. Use the API to list all assets, this test will check that:
    * Immich contains all expected assets
    * Our videos are detected as videos
    * Exif extraction works on both videos and pictures
    * Our VP9 video is transcoded to MPEG4
    * Live/Motion photos are detected
8. Verify that our six people are detected and processed

??? Warning "Hard to match elements in `tests_selenium.py`"
    The generated HTML is a mess, it looks like the sample below. `id` attributes and unique classes are rare.

    > &lt;div class="w-[500px] max-w-[95vw] rounded-3xl border bg-immich-bg p-4 py-8 shadow-sm dark:border-immich-dark-gray dark:bg-immich-dark-gray dark:text-immich-dark-fg"&gt;&lt;div class="flex flex-col place-content-center place-items-center gap-4 px-4 text-immich-primary dark:text-immich-dark-primary"&gt;...

    So I'm forced to use CSS selectors on content, or Beautiful Soup + code to process the DOM to generate unique paths to select against.

    ```python
    self.assert_element("p:contains('CLICK TO UPLOAD YOUR FIRST PHOTO')")
    ```

    ```python
    soup = self.get_beautiful_soup()
    api_keys_div = soup.find(string="API Keys").parent.parent.parent
    api_keys_button = api_keys_div.find("button")
    self.click(css_selector_path(api_keys_button))
    ```

I hope to add more test over time, like more filetypes. If you like to contribute a file with an appropriate license, open an issue.
