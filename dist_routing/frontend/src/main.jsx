import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./index.css";

const DevTools = React.lazy(() => import("./ui/DevTools"));
const Studio = React.lazy(() => import("./ui/Studio"));

const rootNode = document.getElementById("root");
const isStudio = window.location.pathname === "/studio";

ReactDOM.createRoot(rootNode).render(
  <React.StrictMode>
    {isStudio ? (
      <React.Suspense fallback={<div className="min-h-screen flex items-center justify-center bg-[#090d16] text-white">Loading Studio...</div>}>
        <Studio />
      </React.Suspense>
    ) : (
      <App />
    )}
    <React.Suspense fallback={null}>
      <DevTools />
    </React.Suspense>
  </React.StrictMode>
);
