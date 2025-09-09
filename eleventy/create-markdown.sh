#! /bin/bash
# Create all markdown files
# Run from top level directory

inputdir=data/images
if [ ! -d $inputdir ]; then  
    echo "no $inputdir, nothing to do"
fi

trips_dir=data/trips
if [ ! -d $trips_dir ]; then  
    echo "no $tripsdir, nothing to do"
fi
if [ -z "$( ls $trips_dir/*.json )" ]; then
    echo "Empty $tripsdir, nothing to do"
fi

outputdir=eleventy/content
if [ ! -d $outputdir ]; then
    mkdir -p $outputdir
fi

for f in $inputdir/*.json; do
    of=trip-$(basename ${f%.json}).md
    image_weburi=$(jq -r '.WebUri' $f)
    uri=$(jq -r --arg uri $image_weburi '.[]|select(.smugmug==$uri)|.start' $trips_dir/*.json )
    if [ -z $uri ]; then  
        echo "Can't find matching weburi $image_weburi for in trips folder"
    else
        date=$(jq -r --arg uri $image_weburi '.[]|select(.smugmug==$uri)|.start' $trips_dir/*.json )
        tripit=$(jq -r --arg uri $image_weburi '.[]|select(.smugmug==$uri)|.tripit' $trips_dir/*.json )
        uv run eleventy/eleventyfig.py $date $tripit < $f > $outputdir/$of
    fi
done
