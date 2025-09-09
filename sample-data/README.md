Sample data 

This is used for reference when doing the scripts.

Here's how it was generated

```

uv run src/smug-cli.py get-albums > sample-data/albums.json
 uv run src/smug-cli.py get-album-images --album_uri "/api/v2/album/bjvfsZ" > sample-data/album-images.json

uv run src/smug-cli.py get-user
uv run src/smug-cli.py request  --url '/api/v2/user/lmblevins!albums' > sample-data/request-albums.json
uv run src/smug-cli.py request --url '/api/v2/album/bjvfsZ' > sample-data/request-album.json
uv run src/smug-cli.py request --url '/api/v2/album/bjvfsZ!images' > request-images.json
uv run src/smug-cli.py request --url '/api/v2/image/wbHX9Wp-0!sizedetails' > sample-data/request-image-size-details.json
```