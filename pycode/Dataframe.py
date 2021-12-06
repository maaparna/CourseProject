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

for blob in videoblobs:
    blob = videobucket.get_blob(blob.name)
    if blob.name.endswith('.mp4'):
        #print("Blob name is {}".format(blob.name))
        gs_URI = video_uri+blob.name
        #gs_output_URI='gs://aparnajsonfiles'

        operation = video_client.annotate_video(
            input_uri=gs_URI,
            features=['LABEL_DETECTION'],
        )

        result = operation.result(timeout=600)
        filename=blob.name
        """ serialized = result.__class__.to_json(result)

        # write your bucket name in place of bucket1go

        jsonBUCKET = storage_client.get_bucket(jsonbucket_name)
        # store the result as json
        json_result = json.loads(serialized)

        #json_result = result
        annotation_results = result.annotation_results
        date = datetime.now(). strftime("%Y_%m_%d-%I:%M:%S_%p")
        filename=blob.name+date+'.json'
        blob = jsonBUCKET.blob(filename)
            # upload the blob 
        blob.upload_from_string(
                data=json.dumps(json_result),
                content_type='application/json'
                )
        print("Blob name is {} has been uploaded".format(blob.name)) """

        segment_labels = result.annotation_results[0].shot_label_annotations

        Record = namedtuple('File', 'name label start end confidence')

        
        for i, segment_label in enumerate(segment_labels):
            
           # print("Video label description: {}".format(segment_label.entity.description))
            
            # for category_entity in segment_label.category_entities:
            #     print(
            #             "\tLabel category description: {}".format(category_entity.description)
            #         )

            for i, segment in enumerate(segment_label.segments):
                start_time = (segment.segment.start_time_offset.seconds 
                            + segment.segment.start_time_offset.microseconds / 1e6 )
                end_time = (segment.segment.end_time_offset.seconds 
                            + segment.segment.end_time_offset.microseconds / 1e6)
                positions = "{}s to {}s".format(start_time, end_time)
                confidence = segment.confidence
                
                finalrecords.append(Record(
                name =  filename,   
                label = segment_label.entity.description,
                start = start_time,
                end = end_time,
                confidence = confidence
                ))

                
            #     print("\tSegment {}: {}".format(i, positions))
            #     print("\tConfidence: {}".format(confidence))
            # print('\n')

# Capturing the data into a dataframe


for blob in textblobs:
    blob = textbucket.get_blob(blob.name)
    if blob.name.endswith('.mp4'):
        #print("Blob name is {}".format(blob.name))
        gs_URI = text_uri+blob.name
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
                
                if(confidence >=0.99):
                    finalrecords.append(Record(
                    name =  filename,   
                    label = text_label.text,
                    start = start_time,
                    end = end_time,
                    confidence = confidence
                ))

                
            #     print("\tSegment {}: {}".format(i, positions))
            #     print("\tConfidence: {}".format(confidence))
            # print('\n')

    
# Capturing the data into a dataframe
df = pd.DataFrame(finalrecords, columns =['name','label', 'start',  'end', 'confidence'])

# creating a column to calculate the length of the screen time 
df["total"] = df["end"] - df["start"]

df.sort_values(by = "label", inplace = True, ascending = False)

# write your bucket name in place of bucket1go

jsonBUCKET = storage_client.get_bucket(jsonbucket_name)
# store the result as json
json_result = df.to_json(orient = 'records')

#json_result = result
date = datetime.now(). strftime("%Y_%m_%d-%I:%M:%S_%p")
filename='json_file.json'
blob = jsonBUCKET.blob(filename)
    # upload the blob 
blob.upload_from_string(
        data=json.dumps(json_result),
        content_type='application/json'
        )
print("Blob name is {} has been uploaded".format(blob.name))

# # this variable will be used for creating the red vertical line. 
# second_of_interest = 6

# fig = go.Figure()
# for (start, end, label) in zip(df["start"], df["end"], df["label"]):
#     name = label
#     fig.add_trace(go.Scatter(x=[start, end], y=[label, label],
#                     name = name, line=dict(width=4, color = "blue")))
# fig.add_shape(type="line",
#     x0=second_of_interest, y0=0, x1=second_of_interest, y1="beard",
#     line=dict(color="red",width=3)
# )
# fig.update_layout(showlegend=False)    
# fig.show()