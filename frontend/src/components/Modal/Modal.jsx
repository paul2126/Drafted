import React from "react";
import { useModal } from "../../context/ModalContext";
import AbilitySection from "./AbilitySection";
import ActivitySection from "./ActivitySection";

const Modal = () => {
  const { isOpen } = useModal();
  if (!isOpen) return null;

  return (
    <div className="bg-[#e4e8ee] px-[72px] py-[30px]">
      <AbilitySection></AbilitySection>
      <ActivitySection></ActivitySection>
    </div>
  );
};

export default Modal;
