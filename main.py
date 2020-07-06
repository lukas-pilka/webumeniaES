# IMPORTS

import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage
import requests
from requests.auth import HTTPBasicAuth
import json
import config

# CONNECTING TO THE STORAGE

cred = credentials.Certificate("../keys/digital-curator-a894b9b08c2b.json")
firebase_admin.initialize_app(cred, {
    'storageBucket': 'digital-curator.appspot.com'
})

bucket = storage.bucket()

# WRITING TO THE STORAGE FUNCTION

def saveImage(key, imagePath):
    blob = bucket.blob(key)
    outfile = imagePath
    blob.upload_from_filename(outfile)

# CONNECTION TO ELASTIC SEARCH

query = {
    "_source": {
    "includes": ["_id"]
    },
    "query": {
        "term": {
            "has_image": 'true'
        }
    }
}

payload = {'size':100, 'from':0}
rawData = requests.get('https://www.webumenia.sk/api/items_sk/_search', auth=HTTPBasicAuth(config.username, config.password), params=payload, json=query)
rawData.encoding = 'utf-8'
dataDict = json.loads(rawData.text)
artworks = dataDict['hits']['hits']

# CREATING LIST OF IDS

idList = []
for item in artworks:
    idList.append(item['_id'])

# ITERATING THROUGH ID LIST AND DOWNLOADING IMAGES

counter = payload['from']
for id in idList:
    imageUrl = 'https://www.webumenia.sk/dielo/nahlad/' + id + '/800' # creating image url from image id
    imageName = id.replace(":", "-").replace('.', '-').replace('_', '-') + '.jpg' # creating image file name
    img_data = requests.get(imageUrl).content # downloading image
    with open('temp/'+ imageName, 'wb') as handler: # saving image to temp
        handler.write(img_data)
    saveImage('artworks-sk/' + imageName, 'temp/' + imageName) # uploading image to Storage bucket from temp
    os.remove('temp/' + imageName) # deleting image from temp
    print('Downloaded image No. ' + str(counter) + ' from url ' + imageUrl)
    counter += 1







