import { Button } from "@/components/ui/button";
import React from "react";
// Todo: 클릭 시 상태 변경

const getStatusColor = (status) => {
  switch (status) {
    case "submitted":
      return "#ffb38a";
    case "approved":
      return "#3f80f7";
    case "in-progress":
      return "#767676";
    default:
      return "gray-400";
  }
};

const getStatusText = (status) => {
  switch (status) {
    case "submitted":
      return "불합격";
    case "approved":
      return "합격";
    case "in-progress":
      return "작성 중";
    default:
      return "상태";
  }
};

export const StateButton = ({ app }) => {
  // Status button data for mappingconst

  return (
    <Button
      style={{ backgroundColor: getStatusColor(app.status) }}
      className={`w-[168px] flex justify-center `}
    >
      <span className="text-white font-bold">{getStatusText(app.status)}</span>
    </Button>
  );
};
