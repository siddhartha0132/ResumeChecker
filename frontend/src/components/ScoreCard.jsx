const SIGNAL_BG = {
  strong: "rgba(34,197,94,0.15)",
  moderate: "rgba(245,158,11,0.15)",
  weak: "rgba(239,68,68,0.15)",
};
const SIGNAL_BORDER = {
  strong: "rgba(34,197,94,0.4)",
  moderate: "rgba(245,158,11,0.4)",
  weak: "rgba(239,68,68,0.4)",
};
const SIGNAL_TEXT = { strong: "#22c55e", moderate: "#f59e0b", weak: "#ef4444" };

export default function ScoreCard({ score, signal }) {
  const color =
    score >= 70 ? "#22c55e" : score >= 50 ? "#f59e0b" : "#ef4444";

  // Circular arc via SVG
  const radius = 28;
  const circ = 2 * Math.PI * radius;
  const pct = Math.min(score / 100, 1);
  const dash = pct * circ;

  return (
    <div style={{ textAlign: "center", minWidth: 110 }}>
      <svg width={80} height={80} viewBox="0 0 80 80" style={{ display: "block", margin: "0 auto" }}>
        <circle cx={40} cy={40} r={radius} fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth={8} />
        <circle
          cx={40} cy={40} r={radius}
          fill="none"
          stroke={color}
          strokeWidth={8}
          strokeDasharray={`${dash} ${circ - dash}`}
          strokeLinecap="round"
          transform="rotate(-90 40 40)"
          style={{ transition: "stroke-dasharray 0.8s ease" }}
        />
        <text x={40} y={44} textAnchor="middle"
          fill={color} fontSize={18} fontWeight={900} fontFamily="Inter, sans-serif">
          {score}
        </text>
      </svg>
      <div
        style={{
          display: "inline-block", marginTop: 6,
          padding: "3px 12px", borderRadius: 999,
          background: SIGNAL_BG[signal] || "rgba(148,163,184,0.1)",
          border: `1px solid ${SIGNAL_BORDER[signal] || "rgba(148,163,184,0.3)"}`,
          color: SIGNAL_TEXT[signal] || "#94a3b8",
          fontSize: 10, fontWeight: 800, textTransform: "uppercase", letterSpacing: "0.05em",
        }}
      >
        {signal}
      </div>
    </div>
  );
}
