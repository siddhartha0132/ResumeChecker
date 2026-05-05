export default function SkillBadges({
  skills,
  color = "rgba(99,102,241,0.15)",
  textColor = "#818cf8",
  border = "rgba(99,102,241,0.3)",
}) {
  if (!skills || skills.length === 0)
    return <span style={{ fontSize: 12, color: "#475569" }}>None detected</span>;

  return (
    <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
      {skills.map((s) => (
        <span
          key={s}
          style={{
            background: color,
            color: textColor,
            border: `1px solid ${border}`,
            padding: "3px 10px",
            borderRadius: 999,
            fontSize: 11,
            fontWeight: 600,
            letterSpacing: "0.02em",
          }}
        >
          {s}
        </span>
      ))}
    </div>
  );
}
