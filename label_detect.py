from __future__ import print_function
from google.cloud import vision
import os


def detect():
    image_uri = 'https://i.kym-cdn.com/entries/icons/facebook/000/029/959/Screen_Shot_2019-06-05_at_1.26.32_PM.jpg'

    client = vision.ImageAnnotatorClient()
    image = vision.Image()
    image.source.image_uri = image_uri

    response = client.label_detection(image=image)

    str = 'Labels (and confidence score):' + '\n'
    str += '=' * 30
    for label in response.label_annotations:
        str += '\n' + label.description + '(%.2f%%)' % (label.score*100.)
        #str += '<br>' + label.description + '(%.2f%%)' % (label.score*100.)
    return str
