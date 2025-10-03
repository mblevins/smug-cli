# smug-cli
This is the README for Smugmug cli. See also [trip-data](https://github.com/mblevins/trip-data)

This is a CLI written for some specific tasks, not general purpose. It is intended to be easy to add commands to. It runs on Linux, OSX and Windows using WSL. 

The smugmug API reference is [here](https://api.smugmug.com/api/v2/doc/index.html). Follow the steps to get an API key, and put it a file named ~/.smugcli/config.json, in the following format:

```
{
        "api_key": "<api-key>",
        "api_secret": "<api-secret>"
}
```

Run the authorize command, this will prompt for a browser session, and then put an access token in  ~/.smugcli/access.json, which will allow the rest of the commands to run. 

```
uv run src/smug-cli.py authorize
```

The commands are kind of a hodge-podge, the  list-albums, create-rename-list and bulk-rename were used for a renaming project for album name consistency.

## Album lists

The main use of this CLI these days is to create lists of images in albums to use for blog entries (see "Eleventy")

To run everything:

```
bash get-all-album-images.sh
```

This will get all the json files, skipping any that are already there. Note this assumes you're running uv to manage python

If adding a new album, rather than getting images for an old trip, you'll need to delete data/albums.json to force a refresh, otherwise it will skip the new album.

Since this takes a while and rarely change, the files are checked into git

## Eleventy

There's also support for generating an [eleventy](https://www.11ty.dev) blog file with short codes for the images. That should probably be in its own repo, but its here for now.

To create new content:

```
bash eleventy/create-markdown.sh
cp -n eleventy/content/*.md <eleventy-repo>/content/blog
```

There's a trips json file needed for this (see next section), there will be a lot of warnings it can't find a matching weburi, this is normal, just means the trip hasn't been filled out yet


## trip-data

"trip-data" is a required directory, see [here](https://github.com/mblevins/trip-data). If cloning this directory from scratch, then do a "git clone", otherwise do a "git fetch" if finishing up a darktable session with a new trip. If anything changes, commit the changes.  It should probably be a submodule, but I can never remember git submodule commands.




