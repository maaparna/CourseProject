from google.cloud import storage
import pandas as pd
import string
import os, io
import gcsfs
import json
import streamlit as st
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode
# video_return=0
# text_return=0
# def download_blob(bucket_name, destination_file_name):
#     storage_client = storage.Client.from_service_account_json('videointelligence-332009-c6dd45b3cf8f.json')

#     bucket = storage_client.bucket(bucket_name)
#     blobs = storage_client.list_blobs(bucket)

#     for blob in blobs:
#         blob = bucket.blob(blob.name)
#         if blob.name.endswith('.mp4'):
#             #print("Blob name is {}".format(blob.name))
#             blob.download_to_filename(destination_file_name+blob.name)

#     return 1
# # credentials to get access google cloud storage
# # write your key path in place of gcloud_private_key.json
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "videointelligence-332009-c6dd45b3cf8f.json"
jsonbucket_name = 'aparnajsonfiles'
storage_client = storage.Client.from_service_account_json('videointelligence-332009-c6dd45b3cf8f.json')

# videobucket_name='aparnavideointelligence'
# textbucket_name='aparnatextintelligence'

# st.info("Please wait. Downloading the videos....")
# video_return=video_return+download_blob(videobucket_name,'videos/')
# text_return=text_return+download_blob(textbucket_name,'videos/')
# #read the json file stored in cloud storage
# st.balloons()

video_dict = {'cat-in-the-sun_97NNjCKW.mp4':'https://youtu.be/fyJcTn-T5ac',
 'pexels-anna-tarazevich-7008029_IaWpvZ0n.mp4':'https://youtu.be/H8XNJy7th_4',
 'horses-eating-grass_zASTWmx9.mp4':'https://youtu.be/MGgkRmObKg8',
 'bannerg004_piW4SLd3.mp4':'https://youtu.be/vXfi0pNY53Y',
 'Lesson6.9RecommenderSystems.mp4':'https://youtu.be/ph8hz1GBtH8'}

gcs_file_system = gcsfs.GCSFileSystem(project="videointelligence-332009")
gcs_json_path = "gs://aparnajsonfiles/json_file.json"
with gcs_file_system.open(gcs_json_path) as f:
    json_dict = json.load(f)

#convert the json string to pandas dataframe
a_json = json.loads(json_dict)
json_df = pd.DataFrame(a_json, columns=['name', 'label','start','end','confidence'])

json_df=json_df[json_df['confidence'] >= 0.9]

label_option = st.sidebar.selectbox(
    "what label are you searching for?",
    json_df["label"].unique()
)

if(label_option==''):
    selectedjson_df=json_df
    #gb = GridOptionsBuilder.from_dataframe(json_df)
else:
    selectedjson_df=json_df[(json_df['label'] == label_option) & (json_df['confidence'] >= 0.9)]
    #gb = GridOptionsBuilder.from_dataframe(json_df[json_df['label'] == label_option])

selectedjson_df.sort_values(["label", "confidence"], ascending = (True, False))
gb = GridOptionsBuilder.from_dataframe(selectedjson_df)
gb.configure_selection('single')
gb.configure_grid_options(domLayout='normal')
gridOptions = gb.build()
grid_response = AgGrid(selectedjson_df, 
            gridOptions=gridOptions, 
            enable_enterprise_modules=True, 
            allow_unsafe_jscode=True, 
            update_mode=GridUpdateMode.SELECTION_CHANGED)


selected = grid_response['selected_rows']
                    
selected_df = pd.DataFrame(selected ,columns=['name', 'label', 'start', 'end','confidence'])

if not selected_df.empty:
    #st.dataframe(selected_df)
#     last_row_df = selected_df.iloc[-1:]
    video_name_split=str(selected_df['name']).split() 
    video_name=video_name_split[1]
    video_url=video_dict[video_name]
    video_start_split=str(selected_df['start']).split()
    video_start=int(float(video_start_split[1]))
    #print("Video name {}".format(video_name))
    #print("\n")
    #print("Video start {}".format(video_start)) 
    # video_file = open('videos/'+video_name, "rb")
    # video_bytes = video_file.read()
    st.video(video_url, start_time = video_start)





