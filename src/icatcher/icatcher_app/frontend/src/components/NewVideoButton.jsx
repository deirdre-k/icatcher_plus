import { Button } from '@mui/material';

function NewVideoButton(props) {

  const {
    handleButtonClick
  } = props;

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