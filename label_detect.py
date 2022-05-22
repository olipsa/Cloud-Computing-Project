from __future__ import print_function
from google.cloud import vision
import os


def detect():
    image_uri = 'gs://cloud-samples-data/vision/using_curl/shanghai.jpeg'

    client = vision.ImageAnnotatorClient()
    image = vision.Image()
    image.source.image_uri = image_uri

    response = client.label_detection(image=image)

    str = 'Labels (and confidence score):<br>'
    str += '=' * 30
    for label in response.label_annotations:
        str += '<br>' + label.description + '(%.2f%%)' % (label.score*100.)
    return str
