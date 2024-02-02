import pandas as pd

class Study:
    def __init__(self, path, labels, frames):
        self.path = path
        self.labels = labels
        self.frames = frames

    def get_path(self):
        return self.path

    def get_labels(self):
        return self.labels

    def get_frames(self):
        return self.frames

    def edit_frames(self, new_label, start_frame, end_frame = None):
        if end_frame:
            self.labels.iloc[start_frame: end_frame, 3] = new_label 
            self.labels.iloc[start_frame: end_frame, 4] = new_label
        else:
            self.labels.iloc[start_frame, 3] = new_label
            self.labels.iloc[start_frame, 4] = new_label


    
        
    


