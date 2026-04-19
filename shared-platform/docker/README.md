# Purpose

This directory contains Docker support files used by the shared platform layer.

Its role is to keep auxiliary container scripts separated from root-level Docker configuration.

This helps maintain a cleaner repository structure while keeping runtime helpers reusable.

# What goes here

Files in this directory may include:

- entrypoint scripts
- health check scripts
- startup helper scripts
- small reusable Docker runtime utilities

Typical examples:

- `entrypoint.sh`
- `healthcheck.sh`

# What NOT goes here

This directory should NOT contain:

- full application deployment manifests
- Kubernetes files
- Helm charts
- product-specific container logic
- infrastructure scripts tied to one project only