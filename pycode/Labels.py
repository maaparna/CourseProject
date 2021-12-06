import subprocess
import os, io
import pandas as pd
from google.api_core.protobuf_helpers import get_messages
from google.cloud import videointelligence
from collections import namedtuple
import plotly.graph_objects as go
import plotly.express as px
import requests
import string
from google.protobuf.json_format import MessageToJson
from google.cloud import storage
from datetime import datetime
import json

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "videointelligence-332009-c6dd45b3cf8f.json"
video_client = videointelligence.VideoIntelligenceServiceClient()
videobucket_name='aparnavideointelligence'
textbucket_name='aparnatextintelligence'
jsonbucket_name = 'aparnajsonfiles'

video_uri='gs://aparnavideointelligence/'
text_uri='gs://aparnatextintelligence/'
storage_client = storage.Client.from_service_account_json('videointelligence-332009-c6dd45b3cf8f.json')

client = storage.Client()
videobucket = client.bucket(videobucket_name)
videoblobs = client.list_blobs(videobucket_name)

textbucket = client.bucket(textbucket_name)
textblobs = client.list_blobs(textbucket_name)
finalrecords = []

blob = textbucket.get_blob('Lesson6.9RecommenderSystems-CollaborativeFiltering-Part3.mp4')
if blob.name.endswith('.mp4'):
    #print("Blob name is {}".format(blob.name))
    gs_URI = text_uri+'Lesson6.9RecommenderSystems-CollaborativeFiltering-Part3.mp4'
    #gs_output_URI='gs://aparnajsonfiles'

    operation = video_client.annotate_video(
        input_uri=gs_URI,
        features=['TEXT_DETECTION'],
    )

    result = operation.result(timeout=600)
    filename=blob.name

    text_labels = result.annotation_results[0].text_annotations

    Record = namedtuple('File', 'name label start end confidence')

    for i, text_label in enumerate(text_labels):
        
        # print("Video label description: {}".format(text_label.text))
        

        for i, segment in enumerate(text_label.segments):
            start_time = (segment.segment.start_time_offset.seconds 
                        + segment.segment.start_time_offset.microseconds / 1e6 )
            end_time = (segment.segment.end_time_offset.seconds 
                        + segment.segment.end_time_offset.microseconds / 1e6)
            positions = "{}s to {}s".format(start_time, end_time)
            confidence = segment.confidence
            
            finalrecords.append(Record(
            name =  filename,   
            label = text_label.text,
            start = start_time,
            end = end_time,
            confidence = confidence
            ))
            print("Video label description: {}".format(text_label.text))
            print("\tSegment {}: {}".format(i, positions))
            print("\tConfidence: {}".format(confidence))
        print('\n')

# Capturing the data into a dataframe

