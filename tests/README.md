# Immich Distribution Tests

Immich is a rapidly evolving application. I monitor upstream changes and adapt this package accordingly. New releases from the candidate channel are thoroughly tested before being moved to the stable channel, ensuring that stable users encounter no surprises. Automated tests are also run as part of GitHub Actions.

## Running Tests Locally

I assume you have Podman installed; adapting this setup to another OCI runtime (like Docker) should be straightforward. To run the tests inside Incus, prefix the commands with `incus-` (e.g., `make incus-tests`).

### Start Selenium Server

Run `make selenium`. You can access the Selenium browser at http://127.0.0.1:7900 using the password `secret`.

### Run tests

Simply run `make tests`; this command executes the preparation tests (`test-prep`) followed by the main tests (`test-selenium`).

#### Tests: Preparation

This test suite, defined in `tests_prep.py`, sets up the environment for subsequent tests by performing the following actions:

- Registers a new user.
- Executes the initial login and onboarding flows to ensure proper navigation.
- Verifies that the timeline is empty, confirming no pre-existing photo uploads.
- Generates API keys and saves them to a file (`secret.txt`) for use in later tests.

#### Tests: Main Tests

This test suite, defined in `tests_selenium.py`, validates the core functionality of the Immich Distribution application by:

- Uploading various test assets via the API.
- Waiting for image processing jobs to complete and ensuring that the job queue is empty.
- Verifying that assets are uploaded and processed correctly using EXIF data extraction.
- Confirming that people detection functions as expected.

#### Tests: Sync Tests

This test suite, defined in `test_sync.sh`, verifies the synchronization service's functionality by:

- Ensuring that the sync service does not run unexpectedly on a new installation.
- Testing the behavior of the sync service when enabling/disabling synchronization and providing API keys.
- Verifying database modifications via service logs.
- Manipulating files in the user’s sync directory to confirm that asset additions and removals are accurately reflected via the API.
- Ensuring proper deletion and cleanup of assets.
