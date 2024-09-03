---
date: 2024-09-03
author: [nsg]
---

# Breaking change in OAuth

Upstream Immich has this message attached to the release page for Immich 1.113. If you use OAuth with the mobile application you need to update your OAuth provider like below.

> For OAuth users, please replace `app.immich:/` with `app.immich:///oauth-callback` for the Redirect URI in your OAuth provider settings

For more information see the upstream [GitHub issue](https://github.com/immich-app/immich/pull/10832).
