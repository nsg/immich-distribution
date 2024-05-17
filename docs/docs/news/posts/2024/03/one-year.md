---
date: 2024-03-12
authors: [nsg]
categories:
  - Meta
---

# One Year!

Yesterday was the one year mark of Immich Distribution. It's has been a fun and interesting year with a few ups and downs. Let's reflect on the past year and try to guess about the future.

```
commit 72d549a5c0344f89a4173623a3f7eaedab6c54ef
Author: Stefan Berggren
Date:   Sat Mar 11 12:20:32 2023 +0100

   init
```

I have made zero effort to announce the project over the year (except publishing it in the [Snap Store](https://snapcraft.io/immich-distribution)). A slow grow was to my advantage, a year ago I had no idea how hard this would be and I like to stay a little quiet while I test the waters.

The upstream Immich projects developers warned me that it may be hard to automatically upgrade a project like Immich in it's current state. I disagreed and thought that this should be doable. They where happy that I was clear that this was an unofficial package. That was important to me, I had no wish to cause any disturbance to them.

I'm happy to report that I have been able to automatically upgrade every single release except one last summer. A few users had to run a single command manually. It's possible that I was the only one affected because it only affected people with older installations.

I think that Immich popularity has been to my advantage, upstream have been forced to be a little more careful when releaseing breaking changes. Most breaking changes has been changes to the configuration files or database versions. Everyting is packaged inside the snap package in Immich Distribution so that has not been a problem for me.

I have had a few occurrences when I considered giving up, especially when I had to troubleshoot buggy or weird libraries for weeks. Some have been a pain and taken a lot of energy from me. This is someting I do as part of my free time, and when the time and motivation has lacked, progress has been slow.

It has been fun to see the users slowly grow. My snap is _tiny_ compared to the official release, and even small compared to the other community packages. But with zero marketing that is expected! That is something I think will change during 2024, because I intend to spread the word a little!

I also published [a nice graph](/build/statistics) with the 89 Immich releases over the last year! 🤯
