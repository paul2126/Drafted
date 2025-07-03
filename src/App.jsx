import { Suspense } from "react";
import { useRoutes, Routes, Route } from "react-router-dom";
import JobApplicationForm from "./pages/JobApplicationForm.jsx";
import routes from "tempo-routes";
import { ModalProvider } from "./context/ModalContext";
import Modal from "./components/Modal/Modal";
import QuestionInput from "./components/QuestionForm/QuestionInput";

function App() {
  return (
    <Suspense fallback={<p>Loading...</p>}>
      <ModalProvider>
        <Routes>
          <Route path="/" element={<JobApplicationForm />} />
        </Routes>
        {import.meta.env.VITE_TEMPO === "true" && useRoutes(routes)}
      </ModalProvider>
    </Suspense>
  );
}

export default App;
