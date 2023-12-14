import {
  Button
} from '@mui/material';
// import {
//   ChevronLeftRounded,
//   ChevronRightRounded
// } from '@mui/icons-material';
// import { usePlaybackState } from '../../state/PlaybackStateProvider';
// import { useVideoData } from '../../state/VideoDataProvider';
// import styles from './JumpButton.module.css';

function NewVideoButton(props) {

  const {
    handleButtonClick
  } = props;

//   const playbackState = usePlaybackState();
//   const videoData = useVideoData();

  return (
      <Button
          id="newVideo"
          aria-label="upload new video"
          onClick={() => handleButtonClick()}
        >
          Start New Video
      </Button>

  );
}

export default NewVideoButton;