---
date: 2024-01-22 23:40:00
authors: [nsg]
categories:
  - Bugfix
---

# Fix CR2

I noticed that I was unable to process a CR2-file (I _think_ other RAW image formats may have been affected as well). The problem was that libvips fails to difference between TIFF-images and image formats based on top of TIFF like Canons CR2 RAW image format. ImageMagic handles this properly so the fix was to remove TIFF-support from libvips. Libvips will send all unknown formates down to ImageMagic.

ImageMagic is slower compared to libvips so this will slow down TIFF processing a little, but it will fix several RAW image formats. This fix reflects what upstream has done already and I consider it a bug that I missed this when I build my own version of libvips.
