import React from "react";

const StoryBoardButton = ({ className = "" }) => {
  return (
    <img
      src="/storyboard_button.svg"
      alt="Storyboard"
      className="w-[175px] h-[46px]"
    />
  );
};

const StoryLineButton = ({ className = "" }) => {
  return (
    <img
      src="/storyline_button.svg"
      alt="Storyline"
      className="w-[175px] h-[46px]"
    />
  );
};

export { StoryBoardButton, StoryLineButton };
