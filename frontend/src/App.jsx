import "./App.css";
import { useState } from "react";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import StoryLine from "@/routes/StoryLine/StoryLine";
import AppList from "@/routes/AppList/AppList";
import MainPage from "./routes/MainPage.jsx/MainPage";

function App() {
  // const [count, setCount] = useState(0)
  // Routes 목록 안에 Main.jsx, StoryLineDetail.jsx 등 페이지 추가 필요

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<MainPage />} />
        <Route path="/applist" element={<AppList />} />
        <Route path="/storyline" element={<StoryLine />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
