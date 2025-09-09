#! /bin/bash
# Get all albums images. This will skip files if they exist, delete the file to force creation
# (especially albums.json, or it will never add a new album)

encode_filename_escape() {
  local filename="$1"
  # Define special characters to escape
  local special_chars=' !"#$%&'\''()*+,/:;<=>?@[\]^`{|}~'
  local escaped_filename=""

  for (( i=0; i<${#filename}; i++ )); do
    char="${filename:$i:1}"
    if [[ "$special_chars" == *"$char"* ]]; then
      escaped_filename+="\\$char"
    else
      escaped_filename+="$char"
    fi
  done
  echo "$escaped_filename"
}

if [ ! -d data ]; then
    mkdir data
fi
albumfile=data/albums.json

if [ -f $albumfile ]; then 
    echo "$albumfile exists, skipping"
else
    uv run src/smug-cli.py get-albums --pathPrefix "/Travel" > $albumfile
fi

names=$(jq -r '.Album[] | .UrlName' < $albumfile )
for name in $names; do
    imagefile=data/images/${name}.json
    if [ -f $imagefile ]; then
        echo "\"$imagefile\" exists, skipping"
    else
        uri=$(jq  -r --arg name $name '.Album[]|select(.UrlName==$name)|.Uri' < $albumfile)
        uv run src/smug-cli.py get-album-images --album_uri $uri > $imagefile
    fi
done