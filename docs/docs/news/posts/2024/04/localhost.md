---
date: 2024-04-30 17:00:00
authors: [nsg]
---

To increase security, with the release of Immich Distribution `v1.102` and forward, the backend services will no longer listen on all interfaces. They will only bind to `127.0.0.1:3001`, `127.0.0.1:3002` and `127.0.0.1:3003` respectively.

In a less tech-y way. You **must** access Immich Distribution via HAProxy on port `80` (http) or `443` (https). This has always been the supported and expected way to use Immich Distribution so I do not consider this a breaking change. If anyone has the need to access it directly, open an issue and we can discuss a solution for you.
