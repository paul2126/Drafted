import React from "react";

const Logo = ({ className = "" }) => {
  return (
    <img src="/drafted.svg" alt="Logo" className="w-[184.59px] h-[69px]" />
  );
};

const Logout = ({ className = "" }) => {
  return (
    <div className="flex items-center gap-[6px]">
      <img src="/icon.svg" alt="User Icon" className="w-[44px] h-[46px]" />
      <img src="/logout.svg" alt="Logout Icon" className="w-[123px] h-[46px]" />
    </div>
  );
};

export { Logo, Logout };
