from connexion import FlaskApp
from study import Study

import pandas as pd
import os
import hashlib

#Global dictionary storing all studies. id -> study.
STUDIES = {}
FRAME_OFFSET = 3
DEFAULT_ID = '' #FOR TESTING

CURRENT_STUDY = None

def get_hash(path): 
    sha256 = hashlib.sha256()
    sha256.update(path.encode())

    return sha256.hexdigest()

def get_studies():
    return [(id, STUDIES[id]) for id in STUDIES.keys()], 200

def post_study(path_to_study):
    id = get_hash(path_to_study)
    STUDIES[id] = path_to_study

    labels = pd.read_csv(path_to_study + "/labels.txt", header=None)
    labels.columns = ["Frame", "Label", "Confidence"]

    #Setting up Dataframe to support edits.
    labels["Edited"] = "none"
    labels["Merged"] = labels["Label"]
    labels.to_csv(path_to_study + '/audited_labels.txt', index=False)

    frames = [file for file in os.listdir(path + "/decorated_frames")]

    global CURRENT_STUDY
    CURRENT_STUDY = Study(path_to_study, labels, frames) #Set to the current study.
    print(f"Caches new study with path {path_to_study}\n")

    return f"Posted study with path {path_to_study} and id {id}", 200

def get_study(study_id):
    if study_id in STUDIES:
        path = STUDIES[study_id]
        labels = pd.read_csv(path + "/audited_labels.txt", header=None)
        frames = [file for file in os.listdir(path + "/decorated_frames")]
        return f"Study {study_id} has audits {labels} and frames {frames}", 200
    else:
        return f"Study {study_id} does not exist", 404

def post_edit(study_id, frame_range, new_label):
    global CURRENT_STUDY
    if study_id in STUDIES:
        if STUDIES[study_id] != CURRENT_STUDY.get_path(): #Cache the study if not currently cached.
            labels = pd.read_csv(path_to_study + "/audited_labels.txt", header=None)
            frames = [file for file in os.listdir(path + "/decorated_frames")]
            CURRENT_STUDY = Study(STUDIES[study_id], labels, frames)

            print(f"Caches new study with path {STUDIES[study_id]}\n")

        CURRENT_STUDY.edit_frames(frame_range, new_label)
        CURRENT_STUDY.get_labels().to_csv(CURRENT_STUDY.get_path() + '/audited_labels.txt', index=False)

        return f"Study {study_id} has posted the audits", 200
    else:
        return f"Study {study_id} does not exist", 404

#Testing code.
if __name__ == "__main__":
    path = "./../../../../../../Video/frames_with_patch_new/study-57bc591dc0d9d70055f775db_child-111e4f19_video-c6f3fd28_privacy-public_video"
    post_study(path)

    print(CURRENT_STUDY.get_labels().head())
    print(CURRENT_STUDY.get_labels().tail())

    post_edit(DEFAULT_ID, (0, 2), "left")
    print(CURRENT_STUDY.get_labels().head())
    print(CURRENT_STUDY.get_labels().tail())

    new_path = "./../../../../../../Video/frames_with_patch/study-57bc591dc0d9d70055f775db_child-111e4f19_video-c6f3fd28_privacy-public_video"

    post_study(new_path)
    post_edit(DEFAULT_ID, (0, 7), "right")

    print(get_studies())