import "./App.css";
import { useState } from "react";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import StoryLine from "@/routes/StoryLine/StoryLine";
import MainPage from "@/routes/MainPage/MainPage";
import StoryLineDetail from "@/routes/StoryLineDetail/StoryLineDetail";

function App() {
  // const [count, setCount] = useState(0)
  // Routes 목록 안에 Main.jsx, StoryLineDetail.jsx 등 페이지 추가 필요

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<MainPage />} />
        <Route path="/storyline" element={<StoryLine />} />
        <Route path="/storylinedetail" element={<StoryLineDetail />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
