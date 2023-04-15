# Developer Notes

These notes are for me to remember how to configure the development environment and publish the package to PyPI.

## Development Environment

### Install flit

```bash
pip3 install flit
```

### Build and Publish
    
```bash
rm -rf dist; rm -rf build
flit publish
```
