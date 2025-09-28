
Download wheels here before building with `blender --command extension build --source-dir albam/`

```
pip download zstd==1.5.7.2 --dest ./wheels --only-binary=:all: --python-version=3.11 --platform=win_amd64
pip download zstd==1.5.7.2 --dest ./wheels --only-binary=:all: --python-version=3.11 --platform=manylinux_2_17_x86_64
pip download zstd==1.5.7.2 --dest ./wheels --only-binary=:all: --python-version=3.11 --platform=manylinux_2_14_x86_64

# Not yet available on pypi, download from github.com/Brachi/pybc7/
# Download from artifacts in https://github.com/Brachi/pybc7/actions
pip download pybc7 --dest ./wheels --only-binary=:all: --platform=win64
pip download pybc7 --dest ./wheels --only-binary=:all: --platform=linux_x86_64
```
