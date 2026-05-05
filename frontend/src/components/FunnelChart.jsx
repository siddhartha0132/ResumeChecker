import { Bar, Doughnut } from "react-chartjs-2";
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, ArcElement, Tooltip, Legend } from "chart.js";

ChartJS.register(CategoryScale, LinearScale, BarElement, ArcElement, Tooltip, Legend);

export default function FunnelChart({ stages }) {
  const values = [stages[0]||0, stages[1]||0, stages[2]||0, stages[3]||0];
  const colors = ["rgba(99,102,241,0.8)","rgba(168,85,247,0.8)","rgba(245,158,11,0.8)","rgba(34,197,94,0.8)"];

  const barData = {
    labels: ["Applied","ATS Passed","Form Passed","Selected"],
    datasets: [{ label: "Candidates", data: values, backgroundColor: colors, borderRadius: 8, borderSkipped: false }],
  };
  const donutData = {
    labels: ["Selected","Not Selected"],
    datasets: [{ data: [stages[3]||0, (stages[0]||0)-(stages[3]||0)], backgroundColor: ["rgba(34,197,94,0.8)","rgba(255,255,255,0.06)"], borderColor: ["#22c55e","rgba(255,255,255,0.1)"], borderWidth: 2 }],
  };

  const tt = { backgroundColor:"rgba(15,23,42,0.95)", titleColor:"#e2e8f0", bodyColor:"#94a3b8", borderColor:"rgba(99,102,241,0.3)", borderWidth:1 };
  const grid = { color:"rgba(255,255,255,0.04)" };
  const tickStyle = { color:"#64748b", font:{ family:"Inter" } };

  return (
    <div style={{ display:"flex", gap:24, flexWrap:"wrap" }}>
      <div style={{ flex:2, minWidth:280 }}>
        <Bar data={barData} options={{ responsive:true, plugins:{ legend:{display:false}, tooltip:tt }, scales:{ x:{ticks:tickStyle,grid}, y:{ticks:tickStyle,grid} } }} />
      </div>
      <div style={{ flex:1, minWidth:160, maxWidth:200 }}>
        <Doughnut data={donutData} options={{ responsive:true, cutout:"72%", plugins:{ legend:{labels:{color:"#94a3b8",font:{family:"Inter"}}}, tooltip:tt } }} />
        <div style={{ textAlign:"center", marginTop:8, fontSize:12, color:"#475569" }}>
          Rate: {stages[0] ? ((stages[3]/stages[0])*100).toFixed(1) : 0}%
        </div>
      </div>
    </div>
  );
}
