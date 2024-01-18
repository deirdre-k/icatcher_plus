import pandas as pd

FRAME_OFFSET = 4

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

    def edit_frames(self, frame_range, new_label):
        self.labels.iloc[frame_range[0] + FRAME_OFFSET: frame_range[1] + FRAME_OFFSET, 3] = new_label 
        self.labels.iloc[frame_range[0] + FRAME_OFFSET: frame_range[1] + FRAME_OFFSET, 4] = new_label


    
        
    


