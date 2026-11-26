// SPDX-License-Identifier: LicenseRef-MEMORY-NC-Research-1.0
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "@fontsource/zilla-slab/latin-500.css";
import "@fontsource/zilla-slab/latin-600.css";
import "@fontsource/alegreya-sans/latin-400.css";
import "@fontsource/alegreya-sans/greek-400.css";
import "@fontsource/alegreya-sans/latin-400-italic.css";
import "@fontsource/alegreya-sans/latin-500.css";
import "@fontsource/alegreya-sans/greek-500.css";
import "@fontsource/alegreya-sans/latin-700.css";
import { App } from "./App";
import "./style.css";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
