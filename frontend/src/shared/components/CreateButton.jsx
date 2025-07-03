import React from "react";

export const CreateButton = ({ label = "Create +" }) => {
  return (
    <button
      style={{ backgroundColor: "#3f80f7" }}
      className="px-4 py-2  rounded-[20px] text-black font-bold text-lg tracking-wide"
    >
      {label}
    </button>
  );
};
