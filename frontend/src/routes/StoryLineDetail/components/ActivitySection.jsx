import React, { useEffect, useState } from "react";
//import { dummy } from "@/data/dummy";
import axios from "axios";
import { useModal } from "../context/ModalContext";

const ActivitySection = () => {
  //const activities = dummy.activity_list;
  const [activities, setActivities] = useState([]);
  const { isOpen } = useModal();
  const { response } = useModal();

  useEffect(() => {
    const fetchActivityData = async () => {
      try {
        const response = await axios.get(
          "http://54.196.221.162:8000/api/post/"
        );
        const data = response.data;

        if (data.activity_list) {
          setActivities(data.activity_list);
        } else {
          console.warn("activity_list가 응답에 없습니다:", data);
        }
      } catch (error) {
        console.error("ActivitySection API 호출 실패:", error);
      }
    };
    if (isOpen) {
      fetchActivityData(); // 모달이 열렸을 때만 fetch
    }
  }, [response]);

  return (
    <>
      <p className="text-black text-2xl font-medium paperlogy_5 mb-[20px]">
        👍 이 활동으로 문항을 작성해보시는 걸 추천해요 :)
      </p>
      <div className="flex gap-[25px]">
        {activities.map(({ activity, fit, events_list, id }, idx) => (
          <div
            key={id || idx}
            className="bg-white rounded-[15px] shadow-[0px_4px_6px_4px_rgba(0,0,0,0.25)] p-[20px] w-[555px]"
          >
            <div className="flex justify-between items-start mb-[30px]">
              <h3 className="text-black text-[28px] font-semibold paperlogy_6">
                {activity}
              </h3>
              <span className="text-[#ffb38a] text-xl font-semibold paperlogy_6">
                {(fit * 100).toFixed(0)}%
              </span>
            </div>
            <div className="space-y-[25px] mb-[42px]">
              {events_list.map(({ event, id: eventId }, i) => (
                <div
                  key={eventId || i}
                  className="flex justify-between items-center"
                >
                  <p className="text-black text-xl font-normal paperlogy_4">
                    {event}
                  </p>
                  <div className="flex gap-[6px]">
                    <button className="w-[72px] h-[34px] px-[10px] py-[5px] rounded-[15px] text-[#767676] text-xl font-semibold paperlogy_6 flex items-center justify-center">
                      보기
                    </button>
                    <button className="w-[72px] h-[34px] bg-[#3f80f7] px-[10px] py-[5px] rounded-[15px] border-[#767676] text-white text-xl font-semibold paperlogy_6 flex items-center justify-center">
                      선택
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </>
  );
};
export default ActivitySection;
