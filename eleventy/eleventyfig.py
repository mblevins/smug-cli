#! /bin/python
# Read a albums-image json file and output custom elevnty fig short codes
import json
import sys
import re

images=json.load( sys.stdin )

if (len( sys.argv) != 3):
    print("eleventyfig <date> <tripit-url>")
    exit(1)

tripdate=sys.argv[1]
tripit_url=sys.argv[2]


print("---")
print(f"title: {images['UrlName'].replace('-',' ')}")
print(f"date: {tripdate}")
print("draft: true")
print("tags: ['Trips']")
print("---")

print(f"<!-- Tripit URL: {tripit_url} -->\n")
print(f"Full gallery is [here]({images['WebUri']})\n")

for image in images['Images']:
    m=image['ImageSizeDetails'].get('ImageSizeMedium')
    if not m:
        m=image['ImageSizeDetails']['ImageSizeOriginal']
    l=image['ImageSizeDetails'].get('ImageSizeX3Large')
    if not l:
        l=image['ImageSizeDetails']['ImageSizeOriginal']
    print(f"{{% fig \"{image['FileName']}\", \"{m['Url']}\", \"{l['Url']}\", {m['Height']}, {m['Width']}, \"{image['FileName']}\" %}}")
    print("<p>")
