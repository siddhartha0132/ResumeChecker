import { useState } from "react";
import Page1_ATS from "./pages/Page1_ATS";
import Page2_Funnel from "./pages/Page2_Funnel";

const NAV_ITEMS = [
  { id: "ats", label: "⚡ ATS Scorer", sub: "Page 1 — Resume Intelligence" },
  { id: "funnel", label: "🔬 50k Funnel", sub: "Page 2 — Pipeline Automation" },
];

const styles = {
  app: { minHeight: "100vh", background: "#0a0f1e" },
  nav: {
    background: "rgba(15,23,42,0.95)",
    backdropFilter: "blur(12px)",
    borderBottom: "1px solid rgba(99,102,241,0.2)",
    position: "sticky", top: 0, zIndex: 100,
    display: "flex", alignItems: "center", justifyContent: "space-between",
    padding: "0 2rem", height: 64,
  },
  logo: {
    display: "flex", alignItems: "center", gap: 10,
    fontWeight: 900, fontSize: 18, color: "#fff",
    letterSpacing: "-0.5px",
  },
  logoAccent: { color: "#818cf8" },
  badge: {
    background: "rgba(99,102,241,0.15)", border: "1px solid rgba(99,102,241,0.3)",
    color: "#818cf8", borderRadius: 999, padding: "2px 10px", fontSize: 11, fontWeight: 700,
    marginLeft: 8,
  },
  navLinks: { display: "flex", gap: 4 },
  navBtn: (active) => ({
    background: active ? "rgba(99,102,241,0.2)" : "transparent",
    border: active ? "1px solid rgba(99,102,241,0.4)" : "1px solid transparent",
    color: active ? "#818cf8" : "#94a3b8",
    borderRadius: 8, padding: "8px 18px", cursor: "pointer",
    fontWeight: 600, fontSize: 14, transition: "all 0.2s",
    fontFamily: "Inter, sans-serif",
  }),
  content: { padding: "2rem" },
};

export default function App() {
  const [page, setPage] = useState("ats");

  return (
    <div style={styles.app}>
      <nav style={styles.nav}>
        <div style={styles.logo}>
          <span>AntiGravity</span>
          <span style={styles.logoAccent}> × VisionAstraa</span>
          <span style={styles.badge}>v1.0</span>
        </div>
        <div style={styles.navLinks}>
          {NAV_ITEMS.map((n) => (
            <button
              key={n.id}
              style={styles.navBtn(page === n.id)}
              onClick={() => setPage(n.id)}
            >
              {n.label}
            </button>
          ))}
        </div>
        <div style={{ fontSize: 12, color: "#475569" }}>
          Gemini 1.5 Flash · SQLite · FastAPI
        </div>
      </nav>

      <div style={styles.content}>
        {page === "ats" ? <Page1_ATS /> : <Page2_Funnel />}
      </div>
    </div>
  );
}
