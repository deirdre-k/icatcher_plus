from connexion import FlaskApp
from study import Study

import pandas as pd
import os

#Global dictionary storing all studies. id -> study.
STUDIES = {}
FRAME_OFFSET = 3
DEFAULT_ID = '' #FOR TESTING

def get_hash(path): #TO DO: haven't decided how to hash yet.
    return DEFAULT_ID

def get_studies():
    return [(id, STUDIES[id].get_path()) for id in STUDIES.keys()], 200

def post_study(path_to_study):
    id = get_hash(path_to_study)

    labels = pd.read_csv(path_to_study + "/labels.txt", header=None)
    labels.columns = ["Frame", "Label", "Confidence"]

    # #Fixing the offset.
    # labels = labels.iloc[FRAME_OFFSET:].reset_index(drop=True) 
    # labels.Frame -= FRAME_OFFSET

    #Setting up Dataframe to support edits.
    labels["Edited"] = "none"
    labels["Merged"] = labels["Label"]

    frames = [file for file in os.listdir(path + "/decorated_frames")]

    STUDIES[id] = Study(path_to_study, labels, frames) 

    return f"Posted study with path {path_to_study} and id {id}", 200

def get_study(study_id):
    if study_id in STUDIES:
        return f"Study {study_id} has audits {STUDIES[study_id].get_audits()} and frames {STUDIES[study_id].get_frames()}", 200
    else:
        return f"Study {study_id} does not exist", 404

def post_edit(study_id, frame_range, new_label):
    if study_id in STUDIES:
        study = STUDIES[study_id]
        study.edit_frames(frame_range, new_label)
        study.get_labels().to_csv(study.get_path() + '/audited_labels.txt', index=False)

        return f"Study {study_id} has posted the audits", 200
    else:
        return f"Study {study_id} does not exist", 404

# REACT_BUILD_FOLDER = str(
#     Path(Path(__file__).parent.parent, "frontend", "build").absolute()
# )
# REACT_APP_FILE = "index.html"

# app = FlaskApp(__name__, static_folder=REACT_BUILD_FOLDER)
# app.add_api("audited_labels_api.yaml")

if __name__ == "__main__":
    path = "./../../../../../../Video/frames_with_patch_new/study-57bc591dc0d9d70055f775db_child-111e4f19_video-c6f3fd28_privacy-public_video"
    post_study(path)

    print(STUDIES[''].get_labels().head())
    print(STUDIES[''].get_labels().tail())

    post_edit(DEFAULT_ID, (0, 2), "left")
    print(STUDIES[''].get_labels().head())
    print(STUDIES[''].get_labels().tail())
