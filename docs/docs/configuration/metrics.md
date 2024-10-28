# Metrics

Immich supports Prometheus based metrics. You can read more about them over at the [official Immich documentation](https://immich.app/docs/features/monitoring/). You can configure the metrics via two configuration keys. `metrics-telemetry-include` and `metrics-telemetry-exclude`. They map to the environment variables `IMMICH_TELEMETRY_INCLUDE` and `IMMICH_TELEMETRY_EXCLUDE` [documented here](https://immich.app/docs/install/environment-variables#prometheus).

## Examples

```sh title="Enable all metrics"
sudo snap set immich-distribution metrics-telemetry-include="all"
```

```sh title="Enable only api metrics"
sudo snap set immich-distribution metrics-telemetry-include="api"
```

```sh title="Enable all, except api metrics"
sudo snap set immich-distribution metrics-telemetry-include="all"
sudo snap set immich-distribution metrics-telemetry-exclude="api"
```

Mix and match as you see please, available options are `host`, `api`, `io`, `repo`, `job`.
