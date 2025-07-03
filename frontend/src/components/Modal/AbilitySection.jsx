import React from "react";

const AbilitySection = ({ className = "" }) => {
  return (
    <div className="mb-[70px]">
      <p className="text-black text-2xl font-medium paperlogy_5 mb-[30px]">
        😀 이런 역량이 잘 드러나는 활동이 있다면 좋아요!
      </p>
      <div className="space-y-[10px]">
        {[
          {
            title: "협업 능력",
            desc: "다른 사람들과 소통하고 역할을 조율하며 공동의 목표를 이루는 역량",
          },
          {
            title: "자기 인식&성장",
            desc: "자신의 단점을 인정하고 개선하기 위한 구체적인 노력을 통해 성장하는 역량",
          },
          {
            title: "문제 해결력",
            desc: "팀 내 갈등, 역할충돌, 예상치 못한 변수 등에서 효과적으로 대응하는 능력",
          },
        ].map(({ title, desc }, idx) => (
          <div key={idx} className="flex items-center gap-[21px]">
            <div className="w-[169px] h-[50px] bg-[#fafafb] border border-[#767676] rounded-[15px] flex items-center justify-center">
              <span className="text-[#3f80f7] text-[22px] font-medium paperlogy_5">
                {title}
              </span>
            </div>
            <p className="text-black text-xl font-normal font-paperlogy">
              {desc}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default AbilitySection;
