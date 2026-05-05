import SkillBadges from "./SkillBadges";

const SEG_COLOR = { dev:"rgba(99,102,241,0.2)", data:"rgba(168,85,247,0.2)", design:"rgba(34,197,94,0.2)" };
const SEG_TEXT = { dev:"#818cf8", data:"#c084fc", design:"#4ade80" };

export default function CohortTable({ candidates }) {
  if (!candidates?.length) return (
    <div style={{ color:"#334155", textAlign:"center", padding:"40px 0", fontSize:14 }}>No cohort selected yet.</div>
  );

  return (
    <div style={{ overflowX:"auto" }}>
      <table style={{ width:"100%", borderCollapse:"collapse", fontSize:13 }}>
        <thead>
          <tr style={{ borderBottom:"1px solid rgba(255,255,255,0.06)" }}>
            {["#","Name","Score","Signal","Segment","Skills Matched","Summary"].map(h => (
              <th key={h} style={{ padding:"10px 14px", textAlign:"left", color:"#475569", fontWeight:700, fontSize:11, letterSpacing:"0.06em", whiteSpace:"nowrap" }}>{h.toUpperCase()}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {candidates.map((c, i) => {
            const skills = (() => { try { return JSON.parse(c.skills_matched||"[]"); } catch { return []; } })();
            const seg = c.segment || "dev";
            return (
              <tr key={c.id} style={{ borderBottom:"1px solid rgba(255,255,255,0.04)", transition:"background 0.15s" }}
                onMouseEnter={e => e.currentTarget.style.background = "rgba(255,255,255,0.02)"}
                onMouseLeave={e => e.currentTarget.style.background = "transparent"}>
                <td style={{ padding:"12px 14px", color:"#334155", fontWeight:700 }}>{i+1}</td>
                <td style={{ padding:"12px 14px", fontWeight:700, color:"#e2e8f0" }}>{c.name}</td>
                <td style={{ padding:"12px 14px" }}>
                  <span style={{ fontWeight:900, color: c.ats_score>=70?"#22c55e":c.ats_score>=50?"#f59e0b":"#ef4444" }}>{c.ats_score}</span>
                </td>
                <td style={{ padding:"12px 14px" }}>
                  <span style={{ fontSize:10, fontWeight:800, padding:"2px 8px", borderRadius:999,
                    background: c.hire_signal==="strong"?"rgba(34,197,94,0.15)":c.hire_signal==="weak"?"rgba(239,68,68,0.15)":"rgba(245,158,11,0.15)",
                    color: c.hire_signal==="strong"?"#22c55e":c.hire_signal==="weak"?"#ef4444":"#f59e0b" }}>
                    {(c.hire_signal||"moderate").toUpperCase()}
                  </span>
                </td>
                <td style={{ padding:"12px 14px" }}>
                  <span style={{ fontSize:10, fontWeight:700, padding:"2px 10px", borderRadius:999,
                    background:SEG_COLOR[seg], color:SEG_TEXT[seg] }}>{seg.toUpperCase()}</span>
                </td>
                <td style={{ padding:"12px 14px", maxWidth:240 }}>
                  <SkillBadges skills={skills.slice(0,4)} />
                </td>
                <td style={{ padding:"12px 14px", color:"#475569", maxWidth:260, lineHeight:1.5 }}>
                  {(c.summary||"").slice(0,80)}{c.summary?.length>80?"…":""}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
