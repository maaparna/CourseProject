import subprocess
import os, io
import pandas as pd
from google.cloud import videointelligence
from collections import namedtuple
import requests
import string
from google.cloud import storage
from datetime import datetime
import json

#update the key name. This will be the key that you downloaded when you created the service account key.
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "<your-key>.json"
video_client = videointelligence.VideoIntelligenceServiceClient()

#update the bucket name with the bucket that holds the videos you would like use the LABEL_DETECTION on
#more than a video can be stored in this cloud storage.
#it only performs LABEL_DETECTION on these.
videobucket_name='<bucket-name-storing-video-for-label-detection>'

#update the bucket name with the bucket that holds the videos you would like use the TEXT_DETECTION on
#more than a video can be stored in this cloud storage.
#it only performs TEXT_DETECTION on these.
textbucket_name='<bucket-name-storing-video-for-TEXT-detection>'

#update the bucket name with the bucket name where you would like the JSON file to be uploaded.
#This bucket is only used to upload the JSON file
jsonbucket_name = '<bucket-name-for-storing-json-file>'

#update the link with your bucket name that has videos you would like to use the LABEL_DETECTION on
video_uri='gs://<bucket-name-storing-video-for-label-detection>/'

#update the link with your bucket name that has videos you would like to use the TEXT_DETECTION on
text_uri='gs://<bucket-name-storing-video-for-TEXT-detection>/'

#update the key name. This will be the key that you downloaded when you created the service account key.
storage_client = storage.Client.from_service_account_json('<your-key>.json')

client = storage.Client()
videobucket = client.bucket(videobucket_name)
videoblobs = client.list_blobs(videobucket_name)

textbucket = client.bucket(textbucket_name)
textblobs = client.list_blobs(textbucket_name)
finalrecords = []

#Run LABEL_DETECTION on all videos in that bucket
for blob in videoblobs:
    blob = videobucket.get_blob(blob.name)
    if blob.name.endswith('.mp4'):
        gs_URI = video_uri+blob.name

        operation = video_client.annotate_video(
            input_uri=gs_URI,
            features=['LABEL_DETECTION'],
        )

        result = operation.result(timeout=600)
        filename=blob.name

        segment_labels = result.annotation_results[0].shot_label_annotations

        Record = namedtuple('File', 'type name label start end confidence')

        
        for i, segment_label in enumerate(segment_labels):
            
            for i, segment in enumerate(segment_label.segments):
                start_time = (segment.segment.start_time_offset.seconds 
                            + segment.segment.start_time_offset.microseconds / 1e6 )
                end_time = (segment.segment.end_time_offset.seconds 
                            + segment.segment.end_time_offset.microseconds / 1e6)
                positions = "{}s to {}s".format(start_time, end_time)
                confidence = segment.confidence
                
                finalrecords.append(Record(
                type ='video',
                name =  filename,   
                label = segment_label.entity.description,
                start = start_time,
                end = end_time,
                confidence = confidence
                ))

#Run TEXT_DETECTION on all videos in that bucket                
for blob in textblobs:
    blob = textbucket.get_blob(blob.name)
    if blob.name.endswith('.mp4'):
        gs_URI = text_uri+blob.name

        operation = video_client.annotate_video(
            input_uri=gs_URI,
            features=['TEXT_DETECTION'],
        )

        result = operation.result(timeout=600)
        filename=blob.name

        text_labels = result.annotation_results[0].text_annotations

        Record = namedtuple('File', 'type name label start end confidence')

        for i, text_label in enumerate(text_labels):
            
            for i, segment in enumerate(text_label.segments):
                start_time = (segment.segment.start_time_offset.seconds 
                            + segment.segment.start_time_offset.microseconds / 1e6 )
                end_time = (segment.segment.end_time_offset.seconds 
                            + segment.segment.end_time_offset.microseconds / 1e6)
                positions = "{}s to {}s".format(start_time, end_time)
                confidence = segment.confidence
                
                if(confidence >=0.99):
                    finalrecords.append(Record(
                    type='text',
                    name =  filename,   
                    label = text_label.text,
                    start = start_time,
                    end = end_time,
                    confidence = confidence
                ))

    
# Capturing the data into a dataframe
df = pd.DataFrame(finalrecords, columns =['type','name','label', 'start',  'end', 'confidence'])

df["total"] = df["end"] - df["start"]
# I have filtered certain values as the TEXT_DETECTION generates lots of labels that would not make sense. 
# Feel free to comment/uncomment the next four lines to either filter values that you feel are junk
# df=df[~df['label'].str.contains('URBANA')]
# df=df[~df['label'].str.contains('CHAMPAIGN')]
# df=df[~df['label'].str.contains('Department of Computer Science')]
# df=df[~df['label'].str.contains('-')]

df.sort_values(by = "label", inplace = True, ascending = False)

jsonBUCKET = storage_client.get_bucket(jsonbucket_name)
# store the result as json
json_result = df.to_json(orient = 'records')

date = datetime.now(). strftime("%Y_%m_%d-%I:%M:%S_%p")
filename='json_file.json'
blob = jsonBUCKET.blob(filename)
# upload the blob 
blob.upload_from_string(
        data=json.dumps(json_result),
        content_type='application/json'
        )
print("Blob name is {} has been uploaded".format(blob.name))
