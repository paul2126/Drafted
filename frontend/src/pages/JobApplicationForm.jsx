import React, { useState } from "react";
import { Logo, Logout } from "../components/Header";
import { StoryBoardButton, StoryLineButton } from "../components/NavigationBar";
import QuestionInput from "../components/QuestionForm/QuestionInput";
import { useModal } from "../context/ModalContext";
import Modal from "../components/Modal/Modal";

const JobApplicationForm = ({ className = "" }) => {
  return (
    <div className={`w-full max-w-[1280px] mx-auto bg-white ${className}`}>
      <div className="relative">
        <div
          className={`flex justify-between items-center px-[53px] py-[20px] ${className}`}
        >
          <Logo />
          <Logout />
        </div>
        <div className="pt-[35px] pl-[72px]">
          <div className="flex gap-[8px] mb-[8px]">
            <StoryBoardButton></StoryBoardButton>
            <StoryLineButton></StoryLineButton>
          </div>
          <h1 className="text-black text-[45px] font-black font-paperlogy text-left tracking-tight mb-[10px]">
            멋쟁이 사자처럼 13기 지원서
          </h1>
        </div>

        <div className="flex justify-end items-center gap-[15px] px-[53px] pb-[70px]">
          {["문항 1", "문항 2", "문항 3", "문항 4", "+"].map((text, idx) => {
            const isPlus = text === "+";
            const isActive = idx === 0;
            return (
              <div
                key={idx}
                className={`flex items-center justify-center rounded-[15px] border border-[#767676] ${
                  isActive ? "bg-[#ffb38a]" : ""
                } ${isPlus ? "w-[34px] h-[34px]" : "w-[73px] h-[34px]"}`}
              >
                <span
                  className={`text-xl font-semibold font-paperlogy ${
                    isActive ? "text-white" : "text-[#767676]"
                  }`}
                >
                  {text}
                </span>
              </div>
            );
          })}
        </div>
      </div>

      {/* 질문 섹션 */}
      <div className="px-[72px] mt-[40px] mb-[25px]">
        <h2 className="text-black text-[22px] font-semibold font-paperlogy mb-[10px]">
          질문
        </h2>
        <QuestionInput></QuestionInput>
      </div>
      <Modal></Modal>
      {/* 답변 섹션 */}
      <div className="px-[73px] py-[30px]">
        <h2 className="text-black text-[22px] font-semibold font-paperlogy mb-[10px]">
          답변
        </h2>
        <div className="bg-[#fafafb] rounded-[15px] border border-black p-[25px]">
          <div className="space-y-[15px] font-paperlogy text-black text-base">
            {[
              {
                title: "상황 및 과제",
                content:
                  "대학신문사 73대 편집장으로 활동하며 사설 작성 프로세스를 개선한 경험이 있음. 사실 이전부터 사설에 관한 내부 기자들의 불만이 많았음.\n편집장 부임 초기에는 이걸 어떻게 해야 하나 막막해서 적극 개선하지 못했으나, 신입 기자들의 거센 불만 표현으로 개선이 필요하다는 것을 절감.",
              },
              {
                title: "나의 행동",
                content:
                  "기존 부서들의 사설 작성 프로세스를 추적하고 업무 충돌 및 리소스가 과하게 투입되는 지점 확인 및 개선안 도출\n이전 기수 선배들 및 대학신문사에 오랜 머문 간사단과 소통함으로써 제시한 해결책에 적절한 방향성인지 점검\n자문위원 교수 및 행정실에게 사전 문건을 공유하고 두 차례의 전사 내부 회의를 토대로 프로세스 개선에 합의 도출",
              },
              {
                title: "결과 및 성과",
                content:
                  "사설 퇴고가 완료되는 시점이 주말에서 금요일로 1일 단축, 데스크 부담 경감으로 업무 효율성 상승, 기자단 및 자원위원 만족도 상승",
              },
              {
                title: "느낀점 및 포부",
                content:
                  "기존의 방식을 무조건 지키려고 하기보다 효율적으로 대응할 수 있는 방법을 적극적으로 찾아야 한다는 점 느낌, 멋사에서도 그렇게 하겠다",
              },
            ].map(({ title, content }, idx) => (
              <div key={idx}>
                <div className="flex items-center gap-[6px] mb-[6px]">
                  <span className="text-xl">📍</span>
                  <span className="font-semibold">{title}</span>
                </div>
                <div className="bg-white border border-[#d1d5db] rounded-[10px] px-[14px] py-[10px] leading-[24px] whitespace-pre-line">
                  {content}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* 태그 */}
      <div className="px-[70px] pb-[62px]">
        <div className="flex justify-between">
          {[
            "분량에 맞춰 간결하게",
            "자연스러운 문장으로",
            "역량이 잘 드러나게",
            "스토리를 잘 살려서",
          ].map((text, i) => (
            <div
              key={i}
              className={`${
                i === 3 ? "bg-[#ffb38a]" : "bg-[#e4e8ee]"
              } rounded-[15px] border border-black py-[20px] w-[266px] flex items-center justify-center`}
            >
              <span className="text-black text-[22px] font-semibold font-paperlogy">
                {text}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default JobApplicationForm;
