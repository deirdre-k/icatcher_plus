from connexion import FlaskApp
from study import Study

import pandas as pd
import os
import hashlib
import base64

#Global dictionary storing all studies. id -> study.
STUDIES = {}
CURRENT_STUDY = None

#UTILITY FUNCTIONS
def get_hash(path_to_study): 
    sha256 = hashlib.sha256()
    sha256.update(path_to_study.encode())

    return sha256.hexdigest()

def set_current_study(path_to_study):
    global CURRENT_STUDY
    if CURRENT_STUDY.get_path() == path_to_study: #Already the current study
        return True

    directory_items = set(os.listdir(path_to_study))
    if "audited_labels.csv" in directory_items: #Check if the file exists
        labels = pd.read_csv(path_to_study + "/audited_labels.csv")
    else:
        return False
    
    if "decorated_frames" in directory_items:
        frames = []
        frame_files = os.listdir(path_to_study + "/decorated_frames")
        frame_files.sort()
        for file in frame_files:
            image = open(path_to_study + "/decorated_frames/" + file, "rb")
            data = image.read()
            frames.append(base64.b64encode(data).decode('utf-8'))
            image.close()
    else:
        return False

    CURRENT_STUDY = Study(path_to_study, labels, frames)
    return True

#API ENDPOINTS
def get_studies():
    return [{"id": id, "path_to_study": STUDIES[id]} for id in STUDIES.keys()], 200

def post_study(path_to_study):
    try:
        directory_items = set(os.listdir(path_to_study))
    except FileNotFoundError:
        return f"Study with path {path_to_study} is not an existing directory", 400

    if "labels.txt" in directory_items and "decorated_frames" in directory_items: 
        labels = pd.read_csv(path_to_study + "/labels.txt", header=None) 

        frames = []
        frame_files = os.listdir(path_to_study + "/decorated_frames")
        frame_files.sort()
        for file in frame_files: 
            image = open(path_to_study + "/decorated_frames/" + file, "rb")
            data = image.read()
            frames.append(base64.b64encode(data).decode('utf-8'))
            image.close()

        if labels.shape[1] != 3 and labels.shape[0] != len(frames): 
            return f"labels.txt file in {path_to_study} does not have the correct dimensions", 400

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
            current_labels = CURRENT_STUDY.get_labels()

            #Convert to object.
            labels_return = []
            for i in range(len(current_labels)):
                labels_return.append({"label": current_labels.iloc[i, current_labels.columns.get_loc('Label')], 
                                    "confidence": current_labels.iloc[i, current_labels.columns.get_loc('Confidence')], 
                                    "edited": current_labels.iloc[i, current_labels.columns.get_loc('Edited')], 
                                    "merged": current_labels.iloc[i, current_labels.columns.get_loc('Merged')]})

            return {"labels": labels_return, "frames": CURRENT_STUDY.get_frames()}, 200
        else:
            return f"Study {study_id} is an invalid directory", 400
    else:
        return f"Study {study_id} does not exist", 404

def get_frames(study_id, start = None, end = None):
    if study_id in STUDIES:
        if set_current_study(STUDIES[study_id]):
            frames = CURRENT_STUDY.get_frames()
            if start and end: #Range.
                if start >= 0 and end <= len(frames):
                    return frames[start:end], 200
                else:
                    return f"Range from {start} to {end} is invalid", 400
            
            elif start != None: #One frame.
                if start >= 0 and start < len(frames):
                    return frames[start:start+1], 200
                else:
                    return f"Frame at {start} is invalid", 400

            else: #All frames.
                return frames, 200
        
        else:
            return f"Study {study_id} is an invalid directory", 400
    else:
        return f"Study {study_id} does not exist", 404

def get_labels(study_id, start = None, end = None):
    if study_id in STUDIES:
        if set_current_study(STUDIES[study_id]):
            current_labels = CURRENT_STUDY.get_labels()

            if start and end: #Range.
                if start >= 0 and end <= len(current_labels):
                    return [{"label": current_labels.iloc[i, current_labels.columns.get_loc('Label')], 
                                    "confidence": current_labels.iloc[i, current_labels.columns.get_loc('Confidence')], 
                                    "edited": current_labels.iloc[i, current_labels.columns.get_loc('Edited')], 
                                    "merged": current_labels.iloc[i, current_labels.columns.get_loc('Merged')]} for i in range(start, end)], 200
                else:
                    return f"Range from {start} to {end} is invalid", 400

            elif start != None: #One frame.
                if start >= 0 and start < len(current_labels):
                    return [{"label": current_labels.iloc[start, current_labels.columns.get_loc('Label')], 
                                    "confidence": current_labels.iloc[start, current_labels.columns.get_loc('Confidence')], 
                                    "edited": current_labels.iloc[start, current_labels.columns.get_loc('Edited')], 
                                    "merged": current_labels.iloc[start, current_labels.columns.get_loc('Merged')]}], 200
                else:
                    return f"Label at {start} is invalid", 400

            else: #All frames.
                return [{"label": current_labels.iloc[i, current_labels.columns.get_loc('Label')], 
                                "confidence": current_labels.iloc[i, current_labels.columns.get_loc('Confidence')], 
                                "edited": current_labels.iloc[i, current_labels.columns.get_loc('Edited')], 
                                "merged": current_labels.iloc[i, current_labels.columns.get_loc('Merged')]} for i in range(len(current_labels))], 200
        else:
            return f"Study {study_id} is an invalid directory and has not been registered", 400
    else:
        return f"Study {study_id} does not exist", 404

def post_edit(study_id, new_label, start_frame, end_frame = None):
    if study_id in STUDIES:
        if STUDIES[study_id] == CURRENT_STUDY.get_path(): #Check that the id of the request matches the cached study.
            if end_frame:
                if start_frame >= 0 and end_frame <= len(CURRENT_STUDY.get_frames()): #Check that the range is valid.
                    CURRENT_STUDY.edit_frames(new_label, start_frame, end_frame)
                    CURRENT_STUDY.get_labels().to_csv(CURRENT_STUDY.get_path() + '/audited_labels.csv', index=False)             
                else:
                    return f"Frame range from {start_frame} to {end_frame} cannot be edited", 400
                
                return f"Study {study_id} has posted the audits from {start_frame} to {end_frame} with new label {new_label}", 200
            else:
                if start_frame >= 0 and start_frame < len(CURRENT_STUDY.get_frames()):
                    CURRENT_STUDY.edit_frames(new_label, start_frame)
                    CURRENT_STUDY.get_labels().to_csv(CURRENT_STUDY.get_path() + '/audited_labels.csv', index=False)             
                else:
                    return f"Frame at {start_frame} cannot be edited", 400
                
                return f"Study {study_id} has posted the audit at {start_frame} with new label {new_label}", 200

        else: 
            return f"Study {study_id} does not match the current cached study", 400
    else:
        return f"Study {study_id} does not exist", 404

#Testing code.
if __name__ == "__main__":
    path = "./../../../../../../Video/frames_with_patch_new/study-57bc591dc0d9d70055f775db_child-111e4f19_video-c6f3fd28_privacy-public_video"
    if post_study(path)[1] != 200:
        print("Study with path should have been posted")    
    if post_edit(get_hash(path), "left", 0, 2)[1] != 200:
        print("Edit for study with path should have been posted")

    new_path = "./../../../../../../Video/frames_with_patch/study-57bc591dc0d9d70055f775db_child-111e4f19_video-c6f3fd28_privacy-public_video"
    if post_study(new_path)[1] != 200:
        print("Study with new_path should have been posted")
    if post_edit(get_hash(new_path), "right", 0, 7)[1] != 200:
        print("Edit for study with new_path should have been posted")

    if get_study(get_hash(path))[1] != 200:
        print("Should be able to get a study that is already registered")

    #Some error catching tests.
    if post_edit(get_hash(new_path), "away", 10, 20)[1] != 400:
        print("Edit for study should not be posted without getting the study first")

    if post_edit(get_hash(path), "away", -5, 10)[1] != 400: 
        print("Edit for study should not be posted for an invalid range")

    get_labels(get_hash(new_path), 0)