import React, { useState, useEffect, Suspense } from "react";
import { BrowserRouter, Routes, Route, Navigate, useNavigate, useParams, useLocation, Link } from "react-router-dom";
import { UI } from "./ui/components";
import { server } from "./pybridge";
import { useSharedState } from "./store";

const Home = React.lazy(() => import("./Home"));
const About = React.lazy(() => import("./About"));
const Blog = React.lazy(() => import("./Blog"));
const Dashboard = React.lazy(() => import("./Dashboard"));
const Settings = React.lazy(() => import("./Settings"));
const Login = React.lazy(() => import("./Login"));

const PageLoader = () => (
  <div className="min-h-screen flex items-center justify-center bg-[#090d16]">
    <div className="flex flex-col items-center gap-4">
      <div className="w-10 h-10 border-2 border-white/20 border-t-blue-500 rounded-full animate-spin" />
      <span className="text-gray-400 text-sm">Loading...</span>
    </div>
  </div>
);

// Route Guard — redirect ke /login jika belum terautentikasi
function RequireAuth({ children }) {
  const token = localStorage.getItem('pyreact_token')
             || sessionStorage.getItem('pyreact_token');
  const location = useLocation();
  if (!token) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }
  return children;
}

// Global navigate helper — gunakan navigate('/path') dari mana saja
let _navigate = null;
export const navigate = (to) => _navigate && _navigate(to);

function NavigateCapture() {
  _navigate = useNavigate();
  return null;
}

export default function App() {
  return (
    <BrowserRouter>
      <NavigateCapture />
      <Suspense fallback={<PageLoader />}>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/about" element={<About />} />
          <Route path="/blog" element={<Blog />} />
          <Route path="/dashboard" element={<RequireAuth><Dashboard /></RequireAuth>} />
          <Route path="/settings" element={<RequireAuth><Settings /></RequireAuth>} />
          <Route path="/login" element={<Login />} />
          <Route path="*" element={<div className="min-h-screen bg-[#070b13] text-white flex flex-col items-center justify-center gap-4"><h1 className="text-6xl font-bold text-white/20">404</h1><p className="text-gray-400">Halaman tidak ditemukan.</p><a href="/" className="px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded-xl text-sm font-semibold transition text-white">Kembali ke Home</a></div>} />
        </Routes>
      </Suspense>
    </BrowserRouter>
  );
}
