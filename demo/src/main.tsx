// SPDX-License-Identifier: LicenseRef-MEMORY-NC-Research-1.0
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "@fontsource/courier-prime/latin-400.css";
import "@fontsource/courier-prime/latin-700.css";
import "@fontsource/crimson-pro/latin-400.css";
import "@fontsource/crimson-pro/latin-400-italic.css";
import "@fontsource/crimson-pro/latin-600.css";
import { App } from "./App";
import "./style.css";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
