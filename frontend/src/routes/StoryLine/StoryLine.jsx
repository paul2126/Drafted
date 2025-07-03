import React from "react";
import { applications } from "@/data/applications";
import { ApplicationRow } from "./components/";
import { Header, CreateButton } from "@/shared/components/";
import { Search, Filter } from "lucide-react";
import { Link } from "react-router-dom";
import { useNavigate } from "react-router";

const StoryLine = () => {
  return (
    <>
      {/* Header 컴포넌트 추가 */}
      <Header isLogin={true} />

      {/* Title and Actions */}
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-[32px] font-black text-black">MY APPLY</h1>

        <div className="flex items-center gap-3">
          <button className="p-2">
            <Search className="w-[35px] h-[35px] text-gray-600" />
          </button>
          <button className="p-2">
            <Filter className="w-[35px] h-[35px] text-gray-600" />
          </button>
          <CreateButton />
          <CreateButton label={"Delete -"} />
        </div>
      </div>

      {/* Table Header */}
      <div className="flex items-center py-4 border-b-2 border-black mb-1">
        <div className="w-[75px] flex justify-center">
          {/* Checkbox column */}
        </div>
        <div className="w-[435px] text-center">
          <span className="text-xl font-bold text-black">지원서 명</span>
        </div>
        <div className="w-[169px] text-center">
          <span className="text-xl font-bold text-black">지원 마감일</span>
        </div>
        <div className="w-[162px] text-center">
          <span className="text-xl font-bold text-black">카테고리</span>
        </div>
        <div className="w-[168px] text-center">
          <span className="text-xl font-bold text-black">상태</span>
        </div>
      </div>

      {/* Application Rows */}
      <ApplicationRow applications={applications}></ApplicationRow>
    </>
  );
};

export default StoryLine;
