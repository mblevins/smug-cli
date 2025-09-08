#! /bin/python
# Read a albums-image json file and output custom elevnty fig short codes
import json
import sys


images=json.load( sys.stdin )

for image in images['Images']:
    m=image['ImageSizeDetails']['ImageSizeMedium']
    l=image['ImageSizeDetails']['ImageSizeX3Large']
    print(f"{{% fig \"{image['FileName']}\", \"{m['Url']}\", \"{l['Url']}\", {m['Height']}, {m['Width']}, \"caption\" %}}")

