+++
title = "Machine Learning"
+++

# Machine Learning

## Model revision

Immich uses machine learning models for smart search, face recognition and text recognition (OCR). The models themselves come from projects like OpenCLIP, InsightFace and PaddleOCR. The Immich project converts them to the ONNX format and publishes the results on Hugging Face, under the [immich-app](https://huggingface.co/immich-app) organization. You choose which models to use under **Administration ➔ Settings ➔ Machine Learning**, and the machine learning service downloads them from Hugging Face.

Each model on Hugging Face is a Git repository, and the model revision is the branch the service downloads from. There are two:

- `main` holds the original exports. The branch is no longer updated, and is kept as it is so older Immich releases, which always download from `main`, keep working.
- `v2` holds newer exports that use less memory and run faster. They need the inference code added in Immich v3.3, which older releases do not have, so the Immich project published them on a separate branch instead of replacing `main`.

Upstream Immich uses `v2` by default, and so does the snap. Existing smart search and face data keeps working when you switch between them, nothing needs to be re-indexed.

```bash
# Use the original exports
sudo snap set immich-distribution ml-model-revision=main

# Go back to the default
sudo snap unset immich-distribution ml-model-revision

# Check the current setting
sudo snap get immich-distribution ml-model-revision
```

The machine learning service restarts automatically when you change the setting, and downloads the models for the selected revision the next time it needs them.

The models are stored in `/var/snap/immich-distribution/common/cache`, one folder per model. Models from `main` are stored directly in the model folder, and models from `v2` in a `v2` subfolder of it, so switching back and forth does not download the same models twice. If you only use `v2`, you can free disk space by deleting everything except the `v2` subfolder in each model folder.
