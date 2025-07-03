import React from "react";

const ActivitySection = ({ className = "" }) => {
  return (
    <>
      <p className="text-black text-2xl font-medium paperlogy_5 mb-[20px]">
        👍 이 활동으로 문항을 작성해보시는 걸 추천해요 :)
      </p>
      <div className="flex gap-[25px]">
        {[
          {
            title: "대학신문",
            score: "적합도 96%",
            lines: [
              "사설 프로세스 개선",
              "전 기수 대상 홈커밍 프로젝트 기획",
              "콘텐츠 기자직 신설 및 SNS 리브랜딩",
            ],
            buttonColor: "#ffb38a",
          },
          {
            title: "SNEW 학회",
            score: "적합도 93%",
            lines: ["학회 만족도 조사 및 개선 경험", "S2엔터테인먼트 결과보고"],
            buttonColor: "#3f80f7",
          },
        ].map(({ title, score, lines, buttonColor }, idx) => (
          <div
            key={idx}
            className="bg-white rounded-[15px] shadow-[0px_4px_6px_4px_rgba(0,0,0,0.25)] p-[20px] w-[555px]"
          >
            <div className="flex justify-between items-start mb-[30px]">
              <h3 className="text-black text-[28px] font-semibold paperlogy_6">
                {title}
              </h3>
              <span className="text-[#ffb38a] text-xl font-semibold paperlogy_6">
                {score}
              </span>
            </div>
            <div className="space-y-[25px] mb-[42px]">
              {lines.map((line, i) => (
                <div key={i} className="flex justify-between items-center">
                  <p className="text-black text-xl font-normal paperlogy_4">
                    {line}
                  </p>
                  <div className="flex gap-[6px]">
                    <button className="w-[72px] h-[34px] px-[10px] py-[5px] rounded-[15px] border border-[#767676] text-[#767676] text-xl font-semibold paperlogy_6 flex items-center justify-center">
                      보기
                    </button>
                    <button
                      className="w-[72px] h-[34px] px-[10px] py-[5px] rounded-[15px] border border-[#767676] text-white text-xl font-semibold paperlogy_6 flex items-center justify-center"
                      style={{ backgroundColor: buttonColor }}
                    >
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
