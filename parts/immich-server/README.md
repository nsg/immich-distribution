# Immich Server Assets

This folder contains assets used to package the Immich server component as part of the snapcraft build process.

## Contents

- **`patches/`** - Patches applied to the server before building. Some are auto-generated, others manually created.
- **`scripts/`** - Scripts copied into the final image for starting server processes.
- **`src/`** - Source code used to generate patches.
- **`Makefile`** - Used to build patches from source code.