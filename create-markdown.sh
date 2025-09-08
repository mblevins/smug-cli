#! /bin/bash


if [ $# != 1 ]; then
    echo "Usage: $0 <file-to-use>"
    exit 1
fi    
file=$1
echo $file

if [ ! -f "$file" ]; then
    echo "$file doesn't exist"
    exit 1
fi

if [ ! -d md ]; then
    mkdir md
fi
uv run src/smug-cli.py list-albums > albums.json
trips=$(jq -r '.[] | .name' < "$file" )
for trip in $trips; do
    if [ ! -d $trip ]; then
        mkdir $trip
    fi
    album_key=$(jq  -r --arg album_name $trip '.Album[]|select(.Name==$album_name)|.AlbumKey' < albums.json)
    album_url=$(jq  -r --arg album_name $trip '.Album[]|select(.Name==$album_name)|.WebUri' < albums.json)
    if [ -z $album_key ]; then
        echo "Warning: can't find $trip in albums"
    else
        tripit_url=$(jq -r --arg name $trip '.[]|select(.name==$name)|.tripit'  < "$file" )
        start=$(jq -r --arg name $trip '.[]|select(.name==$name)|.start'  < "$file" )
        end=$(jq -r --arg name $trip '.[]|select(.name==$name)|.end'  < "$file" )
        uv run src/smug-cli.py create-photo-md --trip_name $trip --date_from $start --date_to $end --album_key $album_key --tripit_url $tripit_url --album_url $album_url > md/trip-${trip}.md
    fi
done