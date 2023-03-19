# Immich Distribution Tests

Upstream Immich is a fast moving project, I will do what I can to detect changes when I update Immich to a new version. I will inspect upstream changes and adapt them to this package, I will also test the new release from the candidate channel before I push it out to stable to protect stable users from surprises. Finally I run a few automated tested as part of GitHub Actions.

## Selenium

I trigger automated Selenium tests in [tests_selenium.py](https://github.com/nsg/immich-distribution/blob/master/tests/tests_selenium.py). Selenium is a automated browser that uses Immich Web to create users, logs in and uses Immich like a real user. The idea is to find problems before a human do.

A pull request is built, installed and tested with Selenium to find regresions.

### Run it locally

If you have podman installed just type `make`, otherwise it would be easy to adapt to another OCI runtime (like Docker).
