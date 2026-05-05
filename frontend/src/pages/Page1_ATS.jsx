import { useState, useRef, useEffect } from "react";
import axios from "axios";
import ScoreCard from "../components/ScoreCard";
import SkillBadges from "../components/SkillBadges";

const API = "/api/resume";

const S = {
  page: { maxWidth: 1100, margin: "0 auto" },
  hero: {
    background: "linear-gradient(135deg, rgba(99,102,241,0.1) 0%, rgba(168,85,247,0.05) 100%)",
    border: "1px solid rgba(99,102,241,0.2)",
    borderRadius: 20, padding: "32px 36px", marginBottom: 32,
    position: "relative", overflow: "hidden",
  },
  heroGlow: {
    position: "absolute", top: -60, right: -60,
    width: 240, height: 240,
    background: "radial-gradient(circle, rgba(99,102,241,0.15) 0%, transparent 70%)",
    borderRadius: "50%", pointerEvents: "none",
  },
  heroTitle: { fontSize: 32, fontWeight: 900, color: "#fff", letterSpacing: "-0.5px", marginBottom: 6 },
  heroSub: { color: "#94a3b8", fontSize: 15 },
  uploadCard: {
    background: "rgba(15,23,42,0.8)",
    backdropFilter: "blur(12px)",
    border: "1px solid rgba(99,102,241,0.2)",
    borderRadius: 16, padding: 28, marginBottom: 32,
  },
  tabRow: { display: "flex", gap: 8, marginBottom: 20 },
  tab: (active) => ({
    padding: "9px 22px", borderRadius: 10, border: "1px solid",
    borderColor: active ? "rgba(99,102,241,0.5)" : "rgba(255,255,255,0.06)",
    background: active ? "rgba(99,102,241,0.2)" : "rgba(255,255,255,0.03)",
    color: active ? "#818cf8" : "#64748b",
    cursor: "pointer", fontWeight: 700, fontSize: 13,
    fontFamily: "Inter, sans-serif", transition: "all 0.2s",
  }),
  textarea: {
    width: "100%", background: "rgba(255,255,255,0.04)",
    border: "1px solid rgba(255,255,255,0.1)", borderRadius: 10,
    padding: 14, color: "#e2e8f0", fontSize: 13,
    fontFamily: "JetBrains Mono, monospace", resize: "vertical",
    marginBottom: 16, outline: "none", boxSizing: "border-box",
  },
  fileZone: {
    border: "2px dashed rgba(99,102,241,0.3)",
    borderRadius: 12, padding: "28px 20px", textAlign: "center",
    marginBottom: 16, cursor: "pointer",
    background: "rgba(99,102,241,0.03)",
    transition: "border-color 0.2s",
  },
  btnPrimary: {
    padding: "11px 32px",
    background: "linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)",
    color: "#fff", border: "none", borderRadius: 10,
    fontWeight: 800, fontSize: 15, cursor: "pointer",
    fontFamily: "Inter, sans-serif",
    boxShadow: "0 4px 24px rgba(99,102,241,0.3)",
    transition: "opacity 0.2s",
  },
  btnDanger: {
    padding: "11px 20px",
    background: "rgba(239,68,68,0.1)", color: "#f87171",
    border: "1px solid rgba(239,68,68,0.3)", borderRadius: 10,
    fontWeight: 600, fontSize: 14, cursor: "pointer",
    fontFamily: "Inter, sans-serif",
  },
  statsRow: { display: "flex", gap: 16, marginBottom: 28, flexWrap: "wrap" },
  statCard: {
    flex: 1, minWidth: 120,
    background: "rgba(15,23,42,0.8)",
    border: "1px solid rgba(99,102,241,0.15)",
    borderRadius: 14, padding: "18px 20px", textAlign: "center",
  },
  statVal: { fontSize: 30, fontWeight: 900, color: "#818cf8" },
  statLabel: { fontSize: 11, color: "#475569", marginTop: 4, fontWeight: 600 },
  candidateCard: (signal) => ({
    background: "rgba(15,23,42,0.85)",
    backdropFilter: "blur(8px)",
    border: "1px solid rgba(255,255,255,0.06)",
    borderLeft: `4px solid ${signal === "strong" ? "#22c55e" : signal === "weak" ? "#ef4444" : "#f59e0b"}`,
    borderRadius: 16, padding: "24px 28px", marginBottom: 18,
    transition: "border-color 0.2s",
  }),
  rankBadge: {
    display: "inline-block", background: "rgba(99,102,241,0.2)",
    border: "1px solid rgba(99,102,241,0.3)",
    color: "#818cf8", borderRadius: 6, padding: "1px 8px",
    fontSize: 11, fontWeight: 800, marginRight: 8,
  },
  name: { fontSize: 20, fontWeight: 800, color: "#f1f5f9", margin: "4px 0" },
  meta: { fontSize: 12, color: "#475569" },
  sectionLabel: { fontSize: 10, fontWeight: 800, letterSpacing: "0.1em", marginBottom: 6 },
  breakdown: {
    display: "flex", gap: 10, marginTop: 16, flexWrap: "wrap",
  },
  breakdownItem: {
    background: "rgba(255,255,255,0.04)",
    border: "1px solid rgba(255,255,255,0.06)",
    borderRadius: 8, padding: "6px 14px",
  },
  geminiBox: {
    marginTop: 16,
    background: "rgba(99,102,241,0.06)",
    border: "1px solid rgba(99,102,241,0.2)",
    borderLeft: "3px solid #6366f1",
    borderRadius: 10, padding: "12px 16px",
    fontSize: 13, color: "#94a3b8", lineHeight: 1.6,
  },
  emptyState: {
    textAlign: "center", color: "#334155", padding: "72px 0", fontSize: 15,
  },
  spinner: {
    display: "inline-block", width: 18, height: 18,
    border: "2px solid rgba(255,255,255,0.2)",
    borderTop: "2px solid #fff", borderRadius: "50%",
    animation: "spin 0.7s linear infinite",
    marginRight: 8, verticalAlign: "middle",
  },
};

export default function Page1_ATS() {
  const [candidates, setCandidates] = useState([]);
  const [loading, setLoading] = useState(false);
  const [mode, setMode] = useState("pdf");
  const [pastedText, setPastedText] = useState("");
  const [dragOver, setDragOver] = useState(false);
  const fileRef = useRef();

  useEffect(() => {
    axios.get(`${API}/results`).then((r) => setCandidates(r.data)).catch(() => {});
  }, []);

  const processFile = async (file) => {
    const form = new FormData();
    form.append("file", file);
    form.append("jd_id", 1);
    const r = await axios.post(`${API}/upload`, form);
    return r.data;
  };

  const handleUpload = async () => {
    setLoading(true);
    try {
      if (mode === "pdf") {
        const files = fileRef.current?.files;
        if (!files?.length) { alert("Select at least one PDF"); return; }
        for (const file of files) {
          const data = await processFile(file);
          setCandidates((prev) =>
            [...prev.filter(c => c.candidate_id !== data.candidate_id), data]
              .sort((a, b) => b.ats_score - a.ats_score)
          );
        }
      } else {
        if (!pastedText.trim()) { alert("Paste resume text first"); return; }
        const form = new FormData();
        form.append("resume_text", pastedText);
        form.append("jd_id", 1);
        const r = await axios.post(`${API}/upload`, form);
        setCandidates((prev) =>
          [...prev, r.data].sort((a, b) => b.ats_score - a.ats_score)
        );
        setPastedText("");
      }
    } catch (e) {
      alert("Error: " + (e.response?.data?.detail || e.message));
    } finally {
      setLoading(false);
    }
  };

  const handleReset = async () => {
    if (!confirm("Clear all candidates?")) return;
    await axios.delete(`${API}/reset`);
    setCandidates([]);
  };

  const avg = candidates.length
    ? Math.round(candidates.reduce((s, c) => s + c.ats_score, 0) / candidates.length)
    : 0;

  return (
    <div style={S.page}>
      {/* Hero */}
      <div style={S.hero}>
        <div style={S.heroGlow} />
        <div style={S.heroTitle}>⚡ VisionAstraa AI Resume Scorer</div>
        <div style={S.heroSub}>
          Two-layer extraction: NLP/Regex detects skills instantly → Gemini 1.5 Flash validates
          contextually. Upload 5–10 PDFs or paste text.
        </div>
      </div>

      {/* Upload Panel */}
      <div style={S.uploadCard}>
        <div style={S.tabRow}>
          <button style={S.tab(mode === "pdf")} onClick={() => setMode("pdf")}>📄 Upload PDF(s)</button>
          <button style={S.tab(mode === "text")} onClick={() => setMode("text")}>📝 Paste Text</button>
        </div>

        {mode === "pdf" ? (
          <div
            style={{ ...S.fileZone, borderColor: dragOver ? "rgba(99,102,241,0.7)" : "rgba(99,102,241,0.3)" }}
            onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
            onDragLeave={() => setDragOver(false)}
            onDrop={(e) => {
              e.preventDefault(); setDragOver(false);
              fileRef.current.files = e.dataTransfer.files;
            }}
            onClick={() => fileRef.current.click()}
          >
            <div style={{ fontSize: 32, marginBottom: 8 }}>📂</div>
            <div style={{ color: "#64748b", fontSize: 14 }}>
              Drag & drop PDFs here, or <span style={{ color: "#818cf8", fontWeight: 700 }}>click to browse</span>
            </div>
            <div style={{ color: "#334155", fontSize: 12, marginTop: 4 }}>Supports multiple files · Max 10MB each</div>
            <input ref={fileRef} type="file" accept=".pdf" multiple style={{ display: "none" }} />
          </div>
        ) : (
          <textarea
            value={pastedText}
            onChange={(e) => setPastedText(e.target.value)}
            placeholder="Paste full resume text here…"
            rows={9}
            style={S.textarea}
          />
        )}

        <div style={{ display: "flex", gap: 12 }}>
          <button onClick={handleUpload} disabled={loading} style={{ ...S.btnPrimary, opacity: loading ? 0.7 : 1 }}>
            {loading && <span style={S.spinner} />}
            {loading ? "Scoring with Gemini…" : "Score Resumes →"}
          </button>
          {candidates.length > 0 && (
            <button onClick={handleReset} style={S.btnDanger}>🗑 Reset</button>
          )}
        </div>
      </div>

      {/* Stats */}
      {candidates.length > 0 && (
        <div style={S.statsRow}>
          {[
            { label: "Total Uploaded", val: candidates.length, icon: "📋" },
            { label: "Strong Signal", val: candidates.filter(c => c.hire_signal === "strong").length, icon: "💚" },
            { label: "Avg ATS Score", val: avg, icon: "📊" },
            { label: "Top Score", val: Math.max(...candidates.map(c => c.ats_score)), icon: "🏆" },
          ].map(s => (
            <div key={s.label} style={S.statCard}>
              <div style={{ fontSize: 22, marginBottom: 4 }}>{s.icon}</div>
              <div style={S.statVal}>{s.val}</div>
              <div style={S.statLabel}>{s.label}</div>
            </div>
          ))}
        </div>
      )}

      {/* Ranked Candidates */}
      {candidates.length > 0 && (
        <>
          <div style={{ fontSize: 13, color: "#475569", marginBottom: 16, fontWeight: 600 }}>
            RANKED BY ATS SCORE — {candidates.length} CANDIDATE{candidates.length !== 1 ? "S" : ""}
          </div>
          {candidates.map((c, i) => (
            <div key={c.candidate_id || i} style={S.candidateCard(c.hire_signal)}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 16 }}>
                <div style={{ flex: 1 }}>
                  <div>
                    <span style={S.rankBadge}>#{i + 1}</span>
                    <span style={S.name}>{c.name}</span>
                  </div>
                  <div style={S.meta}>
                    {[c.email, c.college, c.experience_years != null && `${c.experience_years}y exp`]
                      .filter(Boolean).join(" · ")}
                  </div>

                  {/* Score breakdown bars */}
                  {c.breakdown && (
                    <div style={S.breakdown}>
                      {Object.entries(c.breakdown).map(([k, v]) => (
                        <div key={k} style={S.breakdownItem}>
                          <span style={{ fontSize: 10, color: "#475569", textTransform: "capitalize" }}>{k} </span>
                          <span style={{ fontWeight: 800, color: "#e2e8f0", fontSize: 13 }}>{v}</span>
                          <span style={{ fontSize: 10, color: "#334155" }}>/
                            {k === "skills" ? "40" : k === "experience" || k === "education" ? "25" : "10"}
                          </span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
                <ScoreCard score={c.ats_score} signal={c.hire_signal} />
              </div>

              {/* NLP Extracted */}
              {c.nlp_skills_extracted?.length > 0 && (
                <div style={{ marginTop: 16 }}>
                  <div style={{ ...S.sectionLabel, color: "#475569" }}>🔍 NLP EXTRACTED SKILLS</div>
                  <SkillBadges skills={c.nlp_skills_extracted} />
                </div>
              )}

              {/* Matched vs Missing */}
              <div style={{ display: "flex", gap: 20, marginTop: 16, flexWrap: "wrap" }}>
                <div style={{ flex: 1, minWidth: 180 }}>
                  <div style={{ ...S.sectionLabel, color: "#22c55e" }}>✅ MATCHED</div>
                  <SkillBadges
                    skills={c.skills_matched}
                    color="rgba(34,197,94,0.1)"
                    textColor="#22c55e"
                    border="rgba(34,197,94,0.25)"
                  />
                </div>
                <div style={{ flex: 1, minWidth: 180 }}>
                  <div style={{ ...S.sectionLabel, color: "#ef4444" }}>❌ MISSING FROM JD</div>
                  <SkillBadges
                    skills={c.skills_missing}
                    color="rgba(239,68,68,0.1)"
                    textColor="#f87171"
                    border="rgba(239,68,68,0.25)"
                  />
                </div>
              </div>

              {/* Gemini summary */}
              {c.summary && (
                <div style={S.geminiBox}>
                  <strong style={{ color: "#818cf8" }}>✨ Gemini: </strong>{c.summary}
                </div>
              )}
            </div>
          ))}
        </>
      )}

      {candidates.length === 0 && !loading && (
        <div style={S.emptyState}>
          <div style={{ fontSize: 48, marginBottom: 12 }}>📄</div>
          <div>Upload 5–10 resumes to see the AI-ranked dashboard.</div>
          <div style={{ fontSize: 13, color: "#1e293b", marginTop: 6 }}>
            Supports PDF upload or paste plain text
          </div>
        </div>
      )}

      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}
