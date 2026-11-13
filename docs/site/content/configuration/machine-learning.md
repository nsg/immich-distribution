+++
title = "Machine Learning"
+++

# Machine Learning

## Model revision

Immich downloads its machine learning models (smart search, face recognition, OCR) from Hugging Face. The models come in two sets of exports: `main`, the original exports, and `v2`, newer exports that run faster on the CPU. Like the upstream Docker Compose file, the snap uses `v2` by default.

```bash
# Use the original exports
sudo snap set immich-distribution ml-model-revision=main

# Go back to the default
sudo snap unset immich-distribution ml-model-revision

# Check the current setting
sudo snap get immich-distribution ml-model-revision
```

The machine learning service restarts automatically when you change the setting, and downloads the models for the selected revision the next time it needs them. The models of each revision are stored separately in `/var/snap/immich-distribution/common/cache`, so switching back and forth does not download the same models twice.
