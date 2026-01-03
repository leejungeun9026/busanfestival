import { Navigate, Route, Routes } from "react-router-dom"
import MainPage from "./pages/MainPage"
import ReadPage from "./pages/ReadPage"

function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/busanfestival/main" replace />} />
      <Route path="/busanfestival/main" element={<MainPage />} />
      <Route path="/busanfestival/read" element={<ReadPage />} />
      <Route path="*" element={<Navigate to="/busanfestival/main" replace />} />
    </Routes>
  )
}

export default App
