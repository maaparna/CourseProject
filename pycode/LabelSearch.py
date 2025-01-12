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

#update the key name. This will be the key that you downloaded when you created the service account key.
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "<your-key>.json"

#update the bucket name with the bucket name where you uploaded the JSON file .
jsonbucket_name = '<bucket-name-for-storing-json-file>'

#update the key name. This will be the key that you downloaded when you created the service account key.
storage_client = storage.Client.from_service_account_json('<your-key>.json')

#I created a dictionary to show the video from a youtube link where I had uploaded the same video. 
#The Key is the [name] column in the json file and the value is the youtube link.
#please update with video names you prefer. 
#Ensure the name of the video uploaded to the Label detection video bucket and text detection video bucket match with key column of this dictionary.
video_dict = {'cat-in-the-sun_97NNjCKW.mp4':'https://youtu.be/fyJcTn-T5ac',
 'pexels-anna-tarazevich-7008029_IaWpvZ0n.mp4':'https://youtu.be/H8XNJy7th_4',
 'horses-eating-grass_zASTWmx9.mp4':'https://youtu.be/MGgkRmObKg8',
 'bannerg004_piW4SLd3.mp4':'https://youtu.be/vXfi0pNY53Y',
 'Lesson6.9RecommenderSystems.mp4':'https://youtu.be/ph8hz1GBtH8'}

#Provide your google cloud project ID. 
gcs_file_system = gcsfs.GCSFileSystem(project="<Your cloud Project ID>)
#This is the json file path. This would be the uploaded json file
gcs_json_path = "gs://<bucket-name-for-storing-json-file>/json_file.json"
with gcs_file_system.open(gcs_json_path) as f:
    json_dict = json.load(f)

#converts json to dataframe
a_json = json.loads(json_dict)
json_df = pd.DataFrame(a_json, columns=['type','name', 'label','start','end','confidence'])

#dataframe to load only the labels related to "TEXT_DETECTION".
text_df=json_df[json_df['type']=='text']

#dataframe to load only the labels related to "LABEL_DETECTION".
object_df=json_df[json_df['type']=='video']

st.sidebar.info('Welcome!! This app allows users to search for content within videos using labels generated by the Google VideoIntelligence API. Two types of content detection has been used: Object/label and Text. Choose an option to see the list of labels under them. From the grid please select a row to view the relevant video from the correct segment')
classify_option=st.sidebar.radio("Do you want to view videos annotated on object or text?",
('object based annotation','Text based annotation',))

st.info('Please select a row from the table to view the video from the correct segment')

#based on the selection of the radio button the labels list displays either the TEXT_DETECTION generated labels or LABEL_DETECTION related labels from the json file.
if(classify_option=='Text based annotation'):
    text_df.sort_values(by = "label", inplace = True, ascending = True)
    label_option = st.sidebar.selectbox(
        "what label are you searching for?",
        text_df['label'].unique()
    )
else:
    object_df.sort_values(by = "label", inplace = True, ascending = True)
    label_option = st.sidebar.selectbox(
        "what label are you searching for?",
        object_df['label'].unique()
    )

#based on the label selection the values in the grid will be updated
if(label_option==''):
    selectedjson_df=object_df
else:
    if(classify_option=='Text based annotation'):
        selectedjson_df=text_df[(text_df['label'] == label_option)]
    
    else:
        selectedjson_df=object_df[(object_df['label'] == label_option)]

#Sorting the records to show the data with highest confidence rate first
#These are the config values for the aggrid. This allows for only a single row to be selected instead of multiple etc.
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

# Display the relevant videos by using the name column from the selected row and getting the youtube link from the dictionary
if not selected_df.empty:
    video_name_split=str(selected_df['name']).split() 
    #doing a split as the aggrid inserts a value "0 " in front of the name column so getting the second value.
    video_name=video_name_split[1]
    video_url=video_dict[video_name]
    #doing a split as the aggrid inserts a value "0 " in front of the start column so getting the second value.
    video_start_split=str(selected_df['start']).split()
    video_start=int(float(video_start_split[1]))

    #display video and start at the correct segment
    st.video(video_url, start_time = video_start)





