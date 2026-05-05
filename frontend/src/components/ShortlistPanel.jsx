import React from 'react';
import { motion } from 'framer-motion';

function ExportButton({ candidates }) {
  const handleExport = () => {
    const rows = [
      ['Rank', 'Name', 'Email', 'Phone', 'Match Score', 'Experience (yrs)', 'EV Level', 'Skills'],
      ...candidates.map(c => [
        c.rank,
        c.name || 'Unknown',
        c.email || '',
        c.phone || '',
        `${c.match_score}%`,
        c.experience_years || 0,
        c.ev_insights?.ev_experience_level || 'entry',
        (c.skills || []).join('; '),
      ]),
    ];
    const csv = rows.map(row => row.map(cell => `"${cell}"`).join(',')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'ev_shortlisted_candidates.csv';
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <button onClick={handleExport} className="btn-secondary flex items-center gap-2 text-sm">
      📥 Export CSV
    </button>
  );
}

export default function ShortlistPanel({ candidates }) {
  if (candidates.length === 0) {
    return (
      <div className="text-center py-20">
        <div className="text-5xl mb-4">⭐</div>
        <h3 className="text-xl font-semibold text-white mb-2">No candidates shortlisted yet</h3>
        <p className="text-gray-500">Go to Rankings and click "Shortlist" on candidates you want to keep.</p>
      </div>
    );
  }

  const avgScore = (candidates.reduce((s, c) => s + c.match_score, 0) / candidates.length).toFixed(1);
  const avgExp   = (candidates.reduce((s, c) => s + (c.experience_years || 0), 0) / candidates.length).toFixed(1);

  const summaryStats = [
    { label: 'Total Shortlisted', value: candidates.length, color: '#00ff88' },
    { label: 'Avg Match Score',   value: `${avgScore}%`,    color: '#60a5fa' },
    { label: 'Avg Experience',    value: `${avgExp} yrs`,   color: '#c084fc' },
  ];

  return (
    <div>
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-xl font-bold text-white">⭐ Shortlisted Candidates</h2>
          <p className="text-gray-500 text-sm mt-1">
            {candidates.length} candidate{candidates.length !== 1 ? 's' : ''} selected for further review
          </p>
        </div>
        <ExportButton candidates={candidates} />
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        {summaryStats.map((s, i) => (
          <motion.div
            key={s.label}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.08 }}
            className="glass-card rounded-xl p-4"
            style={{ borderLeft: `3px solid ${s.color}` }}
          >
            <p className="text-xs text-gray-500 mb-1">{s.label}</p>
            <p className="text-3xl font-bold tabular-nums" style={{ color: s.color }}>{s.value}</p>
          </motion.div>
        ))}
      </div>

      {/* Table */}
      <div className="glass-card rounded-2xl overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr>
              <th>Rank</th>
              <th>Candidate</th>
              <th>Contact</th>
              <th>Match</th>
              <th>EV Level</th>
              <th>Domains</th>
              <th>Top Skills</th>
            </tr>
          </thead>
          <tbody>
            {candidates.map((c) => {
              const domains = c.ev_insights?.relevant_domains || [];
              const level   = c.ev_insights?.ev_experience_level || 'entry';
              const lvlColors = {
                senior: { bg: 'rgba(168,85,247,0.15)', color: '#c084fc' },
                mid:    { bg: 'rgba(59,130,246,0.15)',  color: '#60a5fa' },
                entry:  { bg: 'rgba(156,163,175,0.1)',  color: '#9ca3af' },
              };
              const lc = lvlColors[level];

              return (
                <tr key={c.candidate_id}>
                  <td>
                    <span
                      className="w-8 h-8 rounded-full flex items-center justify-center font-bold text-xs text-black"
                      style={{ background: 'linear-gradient(135deg, #00C853, #00ff88)' }}
                    >
                      #{c.rank}
                    </span>
                  </td>
                  <td>
                    <p className="font-semibold text-white">{c.name || 'Unknown'}</p>
                    {c.experience_years > 0 && (
                      <p className="text-xs text-gray-500">{c.experience_years} yrs exp</p>
                    )}
                  </td>
                  <td>
                    {c.email && <p className="text-gray-400 truncate max-w-[160px] text-xs">{c.email}</p>}
                    {c.phone && <p className="text-gray-500 text-xs">{c.phone}</p>}
                  </td>
                  <td>
                    <div className="flex items-center gap-2">
                      <div className="w-14 rounded-full h-1.5" style={{ background: 'rgba(255,255,255,0.08)' }}>
                        <div
                          className="h-1.5 rounded-full"
                          style={{ width: `${c.match_score}%`, background: 'linear-gradient(90deg, #00C853, #00ff88)' }}
                        />
                      </div>
                      <span className="font-semibold text-white tabular-nums text-xs">{c.match_score}%</span>
                    </div>
                  </td>
                  <td>
                    <span
                      className="text-xs px-2 py-0.5 rounded-full font-semibold"
                      style={{ background: lc.bg, color: lc.color }}
                    >
                      {level.charAt(0).toUpperCase() + level.slice(1)}
                    </span>
                  </td>
                  <td>
                    <div className="flex flex-wrap gap-1">
                      {domains.slice(0, 2).map(d => (
                        <span
                          key={d}
                          className="text-xs px-1.5 py-0.5 rounded-full"
                          style={{ background: 'rgba(0,145,234,0.12)', color: '#60a5fa' }}
                        >
                          {d}
                        </span>
                      ))}
                    </div>
                  </td>
                  <td>
                    <div className="flex flex-wrap gap-1">
                      {(c.skills || []).slice(0, 2).map(skill => (
                        <span
                          key={skill}
                          className="text-xs px-1.5 py-0.5 rounded-full"
                          style={{ background: 'rgba(255,255,255,0.06)', color: '#9ca3af' }}
                        >
                          {skill}
                        </span>
                      ))}
                      {(c.skills || []).length > 2 && (
                        <span className="text-xs text-gray-600">+{c.skills.length - 2}</span>
                      )}
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
