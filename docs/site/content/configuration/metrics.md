+++
title = "Metrics"
+++

# Metrics

Immich supports Prometheus based metrics. You can read more about them over at the [official Immich documentation](https://immich.app/docs/features/monitoring/). You can configure the metrics via two configuration keys. `metrics-telemetry-include` and `metrics-telemetry-exclude`. They map to the environment variables `IMMICH_TELEMETRY_INCLUDE` and `IMMICH_TELEMETRY_EXCLUDE` [documented here](https://immich.app/docs/install/environment-variables#prometheus).

## Examples

{% code(title="Enable all metrics") %}
```sh
sudo snap set immich-distribution metrics-telemetry-include="all"
```
{% end %}

{% code(title="Enable only api metrics") %}
```sh
sudo snap set immich-distribution metrics-telemetry-include="api"
```
{% end %}

{% code(title="Enable all, except api metrics") %}
```sh
sudo snap set immich-distribution metrics-telemetry-include="all"
sudo snap set immich-distribution metrics-telemetry-exclude="api"
```
{% end %}

Mix and match as you please, available options are `host`, `api`, `io`, `repo`, `job`.

## Listen address

When enabled, API metrics are served on port `8081` and microservices metrics on port `8082`, both at `/metrics`. They listen on `0.0.0.0` (all IPv4 interfaces) by default and have no authentication. Use `metrics-bind-address` to change the address. Immich restarts when you change it.

{% code(title="Only allow access from the server itself") %}
```sh
sudo snap set immich-distribution metrics-bind-address="127.0.0.1"
```
{% end %}

{% code(title="Go back to the default") %}
```sh
sudo snap unset immich-distribution metrics-bind-address
```
{% end %}

The value is one IPv4 address of the server, without a port. Unlike the HAProxy bind keys, `*` does not work. The value is not validated: with an address Immich can't listen on, Immich runs as normal but without metrics, and logs no error.

IPv6 addresses, including `::`, do not work in Immich v3.4.2. Every request is answered with `400 Bad Request` because of an [upstream bug](https://github.com/immich-app/immich/issues/33466) that is fixed but not yet released.

This key is specific to Immich Distribution. Upstream Immich serves metrics on the address in `IMMICH_HOST`, which the snap needs to keep on `127.0.0.1` as Immich runs behind HAProxy.
