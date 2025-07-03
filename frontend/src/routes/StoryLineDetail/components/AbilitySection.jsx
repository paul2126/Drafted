import React from "react";
import { dummy } from "@/data/dummy";

const AbilitySection = () => {
  const abilities = dummy.ability_list;
  return (
    <div className="mb-[70px]">
      <p className="text-black text-2xl font-medium paperlogy_5 mb-[30px]">
        😀 이런 역량이 잘 드러나는 활동이 있다면 좋아요!
      </p>
      <div className="space-y-[10px]">
        {abilities.map(({ ability, description }, idx) => (
          <div key={idx} className="flex items-center gap-[21px]">
            <div className="w-[169px] h-[50px] bg-[#fafafb] border border-[#767676] rounded-[15px] flex items-center justify-center">
              <span className="text-[#3f80f7] text-[22px] font-medium paperlogy_5">
                {ability}
              </span>
            </div>
            <p className="text-black text-xl font-normal font-paperlogy">
              {description}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default AbilitySection;
