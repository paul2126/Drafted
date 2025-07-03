import React, { useEffect, useState } from "react";
//import { dummy } from "@/data/dummy";
import axios from "axios";
import { useModal } from "../context/ModalContext";

const AbilitySection = () => {
  //const abilities = dummy.ability_list;
  const [abilities, setAbilities] = useState([]);
  const { isOpen } = useModal();

  useEffect(() => {
    const getPostAPI = async () => {
      try {
        const response = await axios.get("http://localhost:8000/api/post/");
        const data = response.data;

        // ability_list가 존재하는지 확인 후 상태 업데이트
        if (data.ability_list) {
          setAbilities(data.ability_list);
        } else {
          console.warn("ability_list가 응답에 없습니다:", data);
        }
      } catch (error) {
        console.error("API 호출 중 에러 발생:", error);
      }
    };
    if (isOpen) {
      getPostAPI(); // 모달이 열렸을 때만 fetch
    }
  }, [isOpen]);

  return (
    <div className="mb-[70px]">
      <p className="text-black text-2xl font-medium paperlogy_5 mb-[30px]">
        😀 이런 역량이 잘 드러나는 활동이 있다면 좋아요!
      </p>
      <div className="space-y-[10px]">
        {abilities.map(({ ability, description, id }, idx) => (
          <div key={id || idx} className="flex items-center gap-[21px]">
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
