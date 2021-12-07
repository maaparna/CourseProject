# Video segment search
## Table of contents

- [Background](https://github.com/maaparna/CourseProject/edit/main/README.md##Backgroud)
- [Installation](https://github.com/maaparna/CourseProject/edit/main/README.md##Installation)
- [Usage](#Usage)
- [API](#API)
- [Maintainers](#Maintainers)

## Backgroud
All have faced a situation where we would like to have the ability to search through a video to just a particular segment of interest or search through our video archive to find a few specific moments. This project intends to create a search engine that will allow video segment search. 

For this to be possible, the videos need to be enriched with metadata. Metadata is not just the date, location and rich description but also a transcript of the video. If we could annotate any object, Text, or signs that appear in the videos, we could search for specific moments when they occur.

In the project, the [pycode](https://github.com/maaparna/CourseProject/tree/main/pycode) folder has the following python files:
-[jsonCreation.py](https://github.com/maaparna/CourseProject/blob/main/pycode/jsonCreation.py) 
-[LabelSearch.py](https://github.com/maaparna/CourseProject/blob/main/pycode/LabelSearch.py)

[jsonCreation.py](https://github.com/maaparna/CourseProject/blob/main/pycode/jsonCreation.py) can be used to annotate the videos stored in the cloud and to upload the resulting json file back to cloud.It uses the Google video intelligence API to annotate the videos. 

[LabelSearch.py](https://github.com/maaparna/CourseProject/blob/main/pycode/LabelSearch.py) uses the json file along with streamlit.io to produce an application that allows to search segments of the videos using the generated labels.


## Installation


[Create Project, Enable API and create service account](https://cloud.google.com/video-intelligence/docs/common/auth)

[Installing and initializing cloud SDK](https://cloud.google.com/sdk/docs/install?authuser=1)

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
