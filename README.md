# Video segment search
## Table of contents

- [Background](#Backgroud)
- [Installation](#Installation)
- [Usage](#Usage)
- [API](#API)
- [Maintainers](#Maintainers)

## Backgroud
All have faced a situation where we would like to have the ability to search through a video to just a particular segment of interest or search through our video archive to find a few specific moments. This project intends to create a search engine that will allow video segment search. 

For this to be possible, the videos need to be enriched with metadata. Metadata is not just the date, location and rich description but also a transcript of the video. If we could annotate any object, Text, or signs that appear in the videos, we could search for specific moments when they occur.

In the project, the [pycode](https://github.com/maaparna/CourseProject/tree/main/pycode) folder has the following python files:
[jsonCreation.py](https://github.com/maaparna/CourseProject/blob/main/pycode/jsonCreation.py), 
[LabelSearch.py](https://github.com/maaparna/CourseProject/blob/main/pycode/LabelSearch.py)
and one txt file
[Requirement.txt](https://github.com/maaparna/CourseProject/blob/main/pycode/requirements.txt)  

[jsonCreation.py](https://github.com/maaparna/CourseProject/blob/main/pycode/jsonCreation.py) can be used to annotate the videos stored in the cloud and to upload the resulting json file back to cloud.It uses the Google video intelligence API to annotate the videos. 

[LabelSearch.py](https://github.com/maaparna/CourseProject/blob/main/pycode/LabelSearch.py) uses the json file along with streamlit.io to produce an application that allows to search segments of the videos using the generated labels.

[Requirement.txt](https://github.com/maaparna/CourseProject/blob/main/pycode/requirements.txt) lists the required client libraries needed to run LabelSearch.py in Streamlit. This file is needed to be able to deploy the application. 



## Installation


[Create Project, Enable API and create service account](https://cloud.google.com/video-intelligence/docs/common/auth)

[Installing and initializing google cloud SDK](https://cloud.google.com/sdk/docs/install?authuser=1)

[Install the latest version of Python](https://realpython.com/installing-python/#how-to-install-python-on-macos) 

[Use a venv to isolate dependencies](https://cloud.google.com/python/docs/setup#installing_and_using_virtualenv)

Install the client library in the venv

```sh
pip install --upgrade google-cloud-videointelligence
```
install the following client libraries
```sh
pip install pandas
pip install namedtupled
pip install streamlit
pip install streamlit-aggrid
pip install gcsfs
```
In order use the python code and make it work there are few things that needs to be set up apart from the libraries.

Three [cloud storage buckets](https://cloud.google.com/storage/docs/creating-buckets) needs to be created under the project that was created in the installation step. One storage bucket is to store the videos that require LABEL_DETECTION to be applied to it, another bucket to store the videos that require TEXT_DETECTION. Third bucket is to store the resultant json file.
> Note: All three buckets have to be created.

## Usage
Load the required videos. Either the ones that require LABEL_DETECTION or TEXT_DETECTION or both. Now we are ready to generate the json file and view the results through streamlit.io

> Note: Ensure to update jsonCreation.py with the correct key, bucket and URI.

Execute jsonCreation.py to create the json file with all the lables for the videos uploaded

```sh
python3 jsonCreation.py
```
once sucessfull you will get a message "Blob name is json_file.json has been uploaded" on the terminal.
Now that the json file is created we can run the LabelSearch.py to view the results in the streamlit app.
> Note: Update LabelSearch.py with the Key file name, the bucket name from which the JSON  file has to be downloaded. Finally and the most important is to update the <video_dict> variable. This is a key, value pair. Key will be the name of the video that can be found in the "Name" field of the json file(the name of the videos that are being annotated) and the value will be the URL(I used youtube to upload my videos) of the video.


execute the following command to locally run the streamlit app
```sh
streamlit run LabelSearch.py
```
To deploy the streamlit app follow the steps in this [link](https://docs.streamlit.io/streamlit-cloud/get-started/deploy-an-app)

My working app for video segment search can be found [here](https://share.streamlit.io/maaparna/streamlit_demo/main/pycode/printDataframe.py)

