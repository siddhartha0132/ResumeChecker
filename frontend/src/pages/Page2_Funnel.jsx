import { useState, useEffect } from "react";
import axios from "axios";
import FunnelChart from "../components/FunnelChart";
import CohortTable from "../components/CohortTable";

const API = "/api/funnel";

const S = {
  page: { maxWidth: 1100, margin: "0 auto" },
  hero: {
    background: "linear-gradient(135deg,rgba(168,85,247,0.1) 0%,rgba(99,102,241,0.05) 100%)",
    border: "1px solid rgba(168,85,247,0.2)", borderRadius: 20,
    padding: "32px 36px", marginBottom: 32, position: "relative", overflow: "hidden",
  },
  heroGlow: {
    position: "absolute", top: -60, left: -60, width: 240, height: 240,
    background: "radial-gradient(circle,rgba(168,85,247,0.15) 0%,transparent 70%)",
    borderRadius: "50%", pointerEvents: "none",
  },
  title: { fontSize: 32, fontWeight: 900, color: "#fff", letterSpacing: "-0.5px", marginBottom: 6 },
  sub: { color: "#94a3b8", fontSize: 15 },
  statsRow: { display: "flex", gap: 16, marginBottom: 28, flexWrap: "wrap" },
  stat: {
    flex: 1, minWidth: 100, textAlign: "center",
    background: "rgba(15,23,42,0.8)", border: "1px solid rgba(168,85,247,0.15)",
    borderRadius: 14, padding: "18px 16px",
  },
  statVal: { fontSize: 28, fontWeight: 900 },
  statLabel: { fontSize: 10, color: "#475569", marginTop: 4, fontWeight: 700, letterSpacing: "0.06em" },
  card: {
    background: "rgba(15,23,42,0.8)", backdropFilter: "blur(12px)",
    border: "1px solid rgba(255,255,255,0.06)", borderRadius: 16, padding: 28, marginBottom: 24,
  },
  cardTitle: { fontSize: 16, fontWeight: 800, color: "#e2e8f0", marginBottom: 6 },
  cardSub: { fontSize: 12, color: "#475569", marginBottom: 20 },
  stagesRow: { display: "flex", gap: 12, marginBottom: 28, flexWrap: "wrap" },
  stageCard: (color) => ({
    flex: 1, minWidth: 140, background: `rgba(${color},0.08)`,
    border: `1px solid rgba(${color},0.25)`, borderRadius: 12, padding: "18px 20px",
    position: "relative", overflow: "hidden",
  }),
  stageName: { fontSize: 11, fontWeight: 800, color: "#475569", letterSpacing: "0.08em", marginBottom: 6 },
  stageCount: (color) => ({ fontSize: 26, fontWeight: 900, color: `rgb(${color})` }),
  stageArrow: { fontSize: 20, display: "flex", alignItems: "center", color: "#334155", paddingTop: 18 },
  btn: (variant) => ({
    padding: "11px 24px", borderRadius: 10, fontWeight: 800, fontSize: 14,
    fontFamily: "Inter, sans-serif", cursor: "pointer", border: "none", transition: "all 0.2s",
    ...(variant === "primary" ? {
      background: "linear-gradient(135deg,#8b5cf6 0%,#6366f1 100%)",
      color: "#fff", boxShadow: "0 4px 20px rgba(139,92,246,0.3)",
    } : variant === "success" ? {
      background: "linear-gradient(135deg,#22c55e 0%,#16a34a 100%)",
      color: "#fff", boxShadow: "0 4px 20px rgba(34,197,94,0.3)",
    } : variant === "warn" ? {
      background: "rgba(245,158,11,0.15)", color: "#f59e0b",
      border: "1px solid rgba(245,158,11,0.3)",
    } : {
      background: "rgba(99,102,241,0.1)", color: "#818cf8",
      border: "1px solid rgba(99,102,241,0.3)",
    }),
  }),
  btnRow: { display: "flex", gap: 12, flexWrap: "wrap", marginBottom: 28 },
  result: {
    background: "rgba(34,197,94,0.06)", border: "1px solid rgba(34,197,94,0.2)",
    borderRadius: 10, padding: "12px 18px", fontSize: 13, color: "#94a3b8",
    marginBottom: 16, lineHeight: 1.7,
  },
  exportBtn: {
    display: "inline-flex", alignItems: "center", gap: 8,
    padding: "9px 20px", background: "rgba(34,197,94,0.1)",
    color: "#22c55e", border: "1px solid rgba(34,197,94,0.3)",
    borderRadius: 10, fontWeight: 700, fontSize: 13,
    cursor: "pointer", textDecoration: "none",
  },
};

const STAGE_COLORS = ["99,102,241","168,85,247","245,158,11","34,197,94"];
const STAGE_NAMES = ["Stage 0 — Applied","Stage 1 — ATS Passed","Stage 2 — Form Passed","Stage 3 — Selected"];

export default function Page2_Funnel() {
  const [stats, setStats] = useState({ stages: {0:0,1:0,2:0,3:0}, total: 0 });
  const [cohort, setCohort] = useState([]);
  const [log, setLog] = useState([]);
  const [loading, setLoading] = useState("");

  const loadStats = async () => {
    const r = await axios.get(`${API}/stats`);
    setStats(r.data);
  };
  const loadCohort = async () => {
    const r = await axios.get(`${API}/cohort`);
    setCohort(r.data);
  };

  useEffect(() => { loadStats(); loadCohort(); }, []);

  const run = async (label, fn) => {
    setLoading(label);
    try {
      const r = await fn();
      setLog(prev => [{ label, data: r.data, ts: new Date().toLocaleTimeString() }, ...prev]);
      await loadStats();
      if (label === "stage3") await loadCohort();
    } catch (e) {
      setLog(prev => [{ label, error: e.response?.data?.detail || e.message, ts: new Date().toLocaleTimeString() }, ...prev]);
    } finally { setLoading(""); }
  };

  const seedMock = () => run("seed", () => axios.post(`${API}/seed-mock?count=50000`));
  const stage1   = () => run("stage1", () => axios.post(`${API}/stage1`));
  const stage2   = () => run("stage2", () => axios.post(`${API}/stage2`));
  const stage3   = () => run("stage3", () => axios.post(`${API}/stage3`));

  return (
    <div style={S.page}>
      <div style={S.hero}>
        <div style={S.heroGlow} />
        <div style={S.title}>🔬 50,000 Applicant Funnel</div>
        <div style={S.sub}>3-stage diversity-aware pipeline: ATS filter → smart form → final cohort. Click each stage in order.</div>
      </div>

      {/* Stage progress cards */}
      <div style={S.stagesRow}>
        {[0,1,2,3].map((n, i) => (
          <>
            <div key={n} style={S.stageCard(STAGE_COLORS[n])}>
              <div style={S.stageName}>{STAGE_NAMES[n].toUpperCase()}</div>
              <div style={S.stageCount(STAGE_COLORS[n])}>{(stats.stages[n]||0).toLocaleString()}</div>
              <div style={{ fontSize:11, color:"#334155", marginTop:4 }}>candidates</div>
            </div>
            {i < 3 && <div key={`arr-${n}`} style={S.stageArrow}>→</div>}
          </>
        ))}
      </div>

      {/* Action buttons */}
      <div style={S.btnRow}>
        <button style={S.btn("outline")} disabled={!!loading} onClick={seedMock}>
          {loading==="seed" ? "⏳ Seeding…" : "🌱 Seed 50k Mock Applicants"}
        </button>
        <button style={S.btn("primary")} disabled={!!loading} onClick={stage1}>
          {loading==="stage1" ? "⏳ Running…" : "→ Run Stage 1: ATS Filter"}
        </button>
        <button style={S.btn("warn")} disabled={!!loading} onClick={stage2}>
          {loading==="stage2" ? "⏳ Running…" : "→ Run Stage 2: Smart Form"}
        </button>
        <button style={S.btn("success")} disabled={!!loading} onClick={stage3}>
          {loading==="stage3" ? "⏳ Building…" : "→ Build Final Cohort (500)"}
        </button>
      </div>

      {/* Activity log */}
      {log.length > 0 && (
        <div style={{ marginBottom: 24 }}>
          {log.slice(0,4).map((l, i) => (
            <div key={i} style={S.result}>
              <strong style={{ color: l.error ? "#f87171" : "#22c55e" }}>
                [{l.ts}] {l.label.toUpperCase()}
              </strong>{" "}
              {l.error ? `❌ ${l.error}` : JSON.stringify(l.data)}
            </div>
          ))}
        </div>
      )}

      {/* Chart */}
      <div style={S.card}>
        <div style={S.cardTitle}>📊 Pipeline Visualization</div>
        <div style={S.cardSub}>Live funnel counts across all 3 stages</div>
        <FunnelChart stages={stats.stages} />
      </div>

      {/* Stats summary */}
      <div style={S.statsRow}>
        {[
          { label:"TOTAL APPLICANTS", val:(stats.total||0).toLocaleString(), color:"#818cf8" },
          { label:"ATS PASSED", val:(stats.stages[1]||0).toLocaleString(), color:"#c084fc" },
          { label:"FORM PASSED", val:(stats.stages[2]||0).toLocaleString(), color:"#f59e0b" },
          { label:"FINAL COHORT", val:(stats.stages[3]||0).toLocaleString(), color:"#22c55e" },
        ].map(s => (
          <div key={s.label} style={S.stat}>
            <div style={{ ...S.statVal, color: s.color }}>{s.val}</div>
            <div style={S.statLabel}>{s.label}</div>
          </div>
        ))}
      </div>

      {/* Cohort table */}
      {cohort.length > 0 && (
        <div style={S.card}>
          <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center", marginBottom:6 }}>
            <div>
              <div style={S.cardTitle}>🏆 Final Cohort — {cohort.length} Selected</div>
              <div style={S.cardSub}>Diversity-balanced: 50% Dev · 30% Data · 20% Design</div>
            </div>
            <a href={`${API}/export`} style={S.exportBtn} download>
              ⬇ Export CSV
            </a>
          </div>
          <CohortTable candidates={cohort} />
        </div>
      )}
    </div>
  );
}
