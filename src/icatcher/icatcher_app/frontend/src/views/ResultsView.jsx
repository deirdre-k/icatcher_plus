import React from 'react';
import { VideoDataProvider } from '../state/VideoDataProvider';
import { PlaybackStateProvider } from '../state/PlaybackStateProvider';

import Instructions from '../components/Instructions';
import UploadModal from '../components/UploadModal';
import VideoFrame from '../components/video/VideoFrame';
import AnnotationsFrame from '../components/annotations/AnnotationsFrame';
import NewVideoButton from '../components/NewVideoButton'

import styles from './ResultsView.module.css';

function ResultsView() {

  const [ modalOpen, setModalOpen ] = React.useState(true)

  const handleNewVideoClick = () => {
    setModalOpen(true);
  }

  return (
    <VideoDataProvider>
      <PlaybackStateProvider>
        <div className={styles.mainpage}>
          <Instructions />
          <div className={styles.content} >
            <VideoFrame />
            <AnnotationsFrame />  
            <NewVideoButton handleButtonClick={handleNewVideoClick}/>
          </div>
          <UploadModal
            open={modalOpen}
            handleClose={() => setModalOpen(false)}
          />
        </div>
      </PlaybackStateProvider>
    </VideoDataProvider>
  );
}

export default ResultsView;
