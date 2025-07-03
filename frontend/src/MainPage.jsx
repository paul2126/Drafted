import React from "react";
import logo from "../src/assets/logo.png";
import mainImage from "../src/assets/mainpageimage.jpg";
import intro1 from "../src/assets/service_intro1.png";
import intro2 from "../src/assets/service_intro2.png";
import intro3 from "../src/assets/service_intro3.png";

const features = [
  {
    img: intro1,
    title: "한눈에 정리되는\n나의 활동 기록",
    color: "text-black",
  },
  {
    img: intro2,
    title: "나만의 스토리를 담은\n지원서를 쉽고 빠르게!",
    color: "text-primary",
  },
  {
    img: intro3,
    title: "클릭 한 번으로\nAI 맞춤 첨삭",
    color: "text-black",
  },
];

const faq = [
  "Q. 이걸 꼭 써야 하나요? ChatGPT나 Notion과는 무엇이 다른가요?",
  "Q. 지원서 유형이 다양한데, 학회/인턴/공모전 모두 커버되나요?",
  "Q. 내 활동 기록은 어떻게 입력하나요? 자동으로 불러오기도 가능한가요?",
  "Q. 무료로 쓸 수 있나요?",
  "Q. 내 데이터는 안전하게 보관되나요?",
];

export default function MainPage() {
  return (
    <div className="w-full min-h-screen overflow-x-hidden bg-background text-foreground font-paperlogy">
      {/* Header */}
      <header className="flex items-center justify-between max-w-5xl mx-auto py-6 px-4">
        <img src={logo} alt="logo" className="h-12" />
        <div className="flex gap-2">
          <button className="w-32 h-10 rounded-full border border-primary text-primary">
            로그인
          </button>
          <button className="w-32 h-10 rounded-full bg-primary text-white">
            회원가입
          </button>
        </div>
      </header>

      {/* Hero */}
      <section className="relative bg-[#E4E8EE]">
        <div className="grid md:grid-cols-2 max-w-5xl mx-auto">
          {/* Text */}
          <div className="p-10 flex flex-col justify-center gap-6">
            <h1 className="font-abhaya-libre text-primary text-6xl leading-tight">
              Blueprint
              <br />
              Your Story
            </h1>
            <p className="font-semibold">
              Drafted와 함께, 당신의 이야기를 설득력 있게 정리하세요.
            </p>
            <p className="font-light">
              대외활동, 학회, 인턴십 자기소개서까지 — <br /> 나만의 스토리를
              손쉽게 정리하고, 지원서로 완성해드릴게요.
            </p>
          </div>
          {/* Image */}
          <img
            src={mainImage}
            alt="mainpageimage"
            className="w-full h-full object-cover"
          />
        </div>
      </section>

      {/* Features */}
      <section className="max-w-5xl mx-auto py-20 px-4">
        <h2 className="text-center text-3xl font-bold mb-16">
          지원서 작성, 이제 어렵지 않아요
        </h2>
        <div className="flex flex-col md:flex-row justify-between gap-12">
          {features.map(({ img, title, color }) => (
            <div key={title} className="flex flex-col items-center text-center">
              <img
                src={img}
                alt={title}
                className="w-72 h-72 object-cover mb-4"
              />
              <p className={`${color} whitespace-pre-line text-xl`}>{title}</p>
            </div>
          ))}
        </div>
        <div className="flex justify-center mt-16">
          <button className="px-10 py-4 bg-[#ffb38a] rounded-xl text-xl border border-gray-400">
            내 지원서 써보기
          </button>
        </div>
      </section>

      {/* FAQ */}
      <section className="max-w-4xl mx-auto py-20 px-4">
        <h2 className="text-center text-3xl font-bold mb-12">
          자주 묻는 질문들
        </h2>
        <ul className="space-y-4">
          {faq.map((q) => (
            <li
              key={q}
              className="border-b pb-4 flex items-center justify-between"
            >
              <span>{q}</span>
              <span className="text-primary">▼</span>
            </li>
          ))}
        </ul>
      </section>

      {/* Footer */}
      <footer className="bg-[#E4E8EE] py-10">
        <div className="max-w-5xl mx-auto flex flex-col md:flex-row justify-between gap-8 px-4">
          <div>
            <p className="text-sm text-muted/80 leading-6">
              서울대학교 멋쟁이사자처럼
              <br />
              서울 관악구 관악로 1<br />
              고객센터 문의 : dmstjddl02@snu.ac.kr, 010-7125-4081
            </p>
          </div>
          <nav className="flex flex-col md:flex-row gap-4 md:items-start">
            {[
              "개인정보 처리방침",
              "이용약관",
              "제휴문의",
              "고객문의",
              "공지사항",
            ].map((link) => (
              <a
                key={link}
                href="#!"
                className="font-semibold hover:text-primary"
              >
                {link}
              </a>
            ))}
          </nav>
        </div>
      </footer>
    </div>
  );
}
