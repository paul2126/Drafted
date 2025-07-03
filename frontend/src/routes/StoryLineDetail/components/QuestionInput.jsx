import React, { useState } from "react";
import { useModal } from "../context/ModalContext";

const QuestionInput = ({ className = "" }) => {
  const { toggle } = useModal();
  return (
    <div
      className={`bg-[#fafafb] rounded-[15px] border border-black p-[20px] relative ${className}`}
    >
      <textarea
        className="w-full bg-[#fafafb] resize-none text-black text-xl font-semibold paperlogy_6 focus:outline-none"
        defaultValue="협업 과정에서 자신의 장점이 드러났던 경험과 단점을 극복한 경험을 하나씩 소개해주세요."
      />
      <div
        className="absolute right-[20px] top-1/2 transform -translate-y-1/2"
        onClick={toggle}
      >
        <img src="/check.svg" alt="Check icon" className="w-[38px] h-[38px]" />
      </div>
    </div>
  );
};

export default QuestionInput;
