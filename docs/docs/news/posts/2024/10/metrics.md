---
date: 2024-10-28
author: [nsg]
---

# Breaking change in Metrics Configuration

The upstream Immich project has changed the configuration format for metrics in the [v1.119.0 release](https://github.com/immich-app/immich/releases/tag/v1.119.0). You will be affected if you have enabled `metrics-enabled` and configured `metrics-api-enabled`, `metrics-host-enabled`, `metrics-io-enabled` or `metrics-job-enabled` to limit collected telemetries.

Check out the [metrics documentation](/configuration/metrics) for more information.
