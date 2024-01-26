from connexion import FlaskApp
from study import Study

import pandas as pd
import os
import hashlib

#Global dictionary storing all studies. id -> study.
STUDIES = {}
DEFAULT_ID = '' #FOR TESTING

CURRENT_STUDY = None

#UTILITY FUNCTIONS
def get_hash(path): 
    sha256 = hashlib.sha256()
    sha256.update(path.encode())

    return sha256.hexdigest()

def set_current_study(path):
    directory_items = set(os.listdir(path))
    if "audited_labels.csv" in directory_items: #Check if the file exists
        labels = pd.read_csv(path + "/audited_labels.csv", header=None)
    else:
        return False
    
    if "decoarated_frames" in directory_items:
        frames = [file for file in os.listdir(path + "/decorated_frames")]
    else:
        return False

    global CURRENT_STUDY
    CURRENT_STUDY = Study(path, labels, frames)
    return True

#API ENDPOINTS
def get_studies():
    return [{"id": id, "path_to_study": STUDIES[id]} for id in STUDIES.keys()], 200

def post_study(path_to_study):
    directory_items = set(os.listdir(path_to_study))

    if "labels.txt" in directory_items and "decorated_frames" in directory_items: 
        labels = pd.read_csv(path_to_study + "/labels.txt", header=None) 
        frames = [file for file in os.listdir(path_to_study + "/decorated_frames")]

        if labels.shape[1] != 3 and labels.shape[0] != len(frames): 
            return f"labels.txt file in {path_to_study} does not have the correct dimensions"

        #Setting up Dataframe to support edits.
        labels.columns = ["Frame", "Label", "Confidence"]
        labels["Edited"] = None
        labels["Merged"] = labels["Label"]
        labels.to_csv(path_to_study + '/audited_labels.csv', index=False)
    else:
        return f"Study with path {path_to_study} is invalid", 400

    global CURRENT_STUDY
    CURRENT_STUDY = Study(path_to_study, labels, frames) #Set to the current study.

    id = get_hash(path_to_study) #Register study if successful.
    STUDIES[id] = path_to_study

    return f"Posted study with path {path_to_study} and id {id}", 200

def get_study(study_id):
    if study_id in STUDIES:
        if set_current_study(STUDIES[study_id]):
            return {"labels": CURRENT_STUDY.get_labels(), "frames": CURRENT_STUDY.get_frames()}, 200
        else:
            return f"Study {study_id} is an invalid directory", 400
    else:
        return f"Study {study_id} does not exist", 404

def post_edit(study_id, frame_range, new_label):
    if study_id in STUDIES:
        if STUDIES[study_id] != CURRENT_STUDY.get_path(): #Cache the study if not currently cached.
            if frame_range[0] >= 0 and frame_range[1] < len(CURRENT_STUDY.get_frames()): #Check that the range is valid.
                CURRENT_STUDY.edit_frames(frame_range, new_label)
                CURRENT_STUDY.get_labels().to_csv(CURRENT_STUDY.get_path() + '/audited_labels.csv', index=False) 
            else:
                return f"Frame range from {frame_range[0]} to {frame_range[1]} cannot be edited", 400
        else: 
            return f"Study {study_id} does not match the current cached study", 400

        return f"Study {study_id} has posted the audits from {frame_range[0]} to {frame_range[1]} with new label {new_label}", 200
    else:
        return f"Study {study_id} does not exist", 404

#Testing code.
if __name__ == "__main__":
    path = "./../../../../../../Video/frames_with_patch_new/study-57bc591dc0d9d70055f775db_child-111e4f19_video-c6f3fd28_privacy-public_video"
    post_study(path)

    print(CURRENT_STUDY.get_labels().head())
    print(CURRENT_STUDY.get_labels().tail())

    print(os.listdir(path))

    post_edit(DEFAULT_ID, (0, 2), "left")
    print(CURRENT_STUDY.get_labels().head())
    print(CURRENT_STUDY.get_labels().tail())

    new_path = "./../../../../../../Video/frames_with_patch/study-57bc591dc0d9d70055f775db_child-111e4f19_video-c6f3fd28_privacy-public_video"

    post_study(new_path)
    post_edit(DEFAULT_ID, (0, 7), "right")

    print(get_studies())