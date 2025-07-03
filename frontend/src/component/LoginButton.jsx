import React from "react";
import logo from "../src/assets/logo.png";

const LoginButton = () => {
  return (
    <header className="flex items-center justify-between max-w-6xl mx-auto py-6 px-4">
      {/* 로고 */}
      <img src={logo} alt="logo" className="h-12" />

      {/* 버튼들 */}
      <div className="flex gap-2">
        <button className="w-32 h-10 rounded-full border border-primary text-primary hover:bg-primary/10 transition">
          로그인
        </button>
        <button className="w-32 h-10 rounded-full bg-primary text-white hover:bg-primary/80 transition">
          회원가입
        </button>
      </div>
    </header>
  );
};

export default LoginButton;
