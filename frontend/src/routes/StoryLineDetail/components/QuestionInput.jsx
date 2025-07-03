import React, { useState } from "react";
import { useModal } from "../context/ModalContext";
import axios from "axios";

import AbilitySection from "./AbilitySection";
import ActivitySection from "./ActivitySection";

const QuestionInput = ({ className = "", applicationId, questionId }) => {
  const { toggle } = useModal();
  const [questionText, setQuestionText] = useState(
    "협업 과정에서 자신의 장점이 드러났던 경험과 단점을 극복한 경험을 하나씩 소개해주세요."
  );
  const { response, setResponse } = useModal();
  const handleSubmit = async () => {
    try {
      const response = await axios.post(
        "http://54.196.221.162:8000/api/ai/analyze/",
        {
          application_id: applicationId,
          question_id: questionId,
          question: questionText,
        }
      );
      console.log(response);
      setResponse(response);
      toggle(); // 모달 열기 or 닫기
    } catch (error) {
      console.error("질문 전송 실패:", error);
    }
  };
  return (
    <div
      className={`bg-[#fafafb] rounded-[15px] border border-black p-[20px] relative ${className}`}
    >
      <textarea
        className="w-full bg-[#fafafb] resize-none text-black text-xl font-semibold paperlogy_6 focus:outline-none"
        value={questionText}
        onChange={(e) => setQuestionText(e.target.value)}
      />
      <div
        className="absolute right-[20px] top-1/2 transform -translate-y-1/2"
        onClick={handleSubmit}
      >
        <img src="/check.svg" alt="Check icon" className="w-[38px] h-[38px]" />
      </div>
    </div>
  );
};

export default QuestionInput;
