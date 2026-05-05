import React from 'react';
import { motion } from 'framer-motion';

function Bar({ value, color = '#00C853' }) {
  return (
    <div className="w-full bg-gray-100 rounded-full h-2 mt-1">
      <motion.div
        className="h-2 rounded-full"
        style={{ background: color }}
        initial={{ width: 0 }}
        animate={{ width: `${value ?? 0}%` }}
        transition={{ duration: 0.7 }}
      />
    </div>
  );
}

export default function ComparisonView({ candidates, onClose }) {
  if (!candidates || candidates.length < 2) return null;

  const metrics = [
    { key: 'match_score',  label: 'Overall Match',    color: '#00C853', icon: '🎯' },
    { key: 'tfidf_score',  label: 'Text Relevance',   color: '#2979FF', icon: '📄' },
    { key: 'skill_score',  label: 'Skill Match',      color: '#00C853', icon: '🔧' },
    { key: 'exp_score',    label: 'Experience',        color: '#c084fc', icon: '📅' },
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: -16 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-2xl shadow-xl border border-gray-200 p-6 mb-6"
    >
      <div className="flex justify-between items-center mb-5">
        <h3 className="text-lg font-heading font-bold text-gray-800">
          🔍 Candidate Comparison ({candidates.length})
        </h3>
        <button onClick={onClose} className="text-gray-400 hover:text-gray-600 text-sm">✕ Close</button>
      </div>

      {/* Names header */}
      <div className="grid gap-4 mb-4" style={{ gridTemplateColumns: `140px repeat(${candidates.length}, 1fr)` }}>
        <div />
        {candidates.map(c => (
          <div key={c.candidate_id} className="text-center">
            <div className="w-10 h-10 rounded-full bg-ev-primary text-white flex items-center justify-center font-bold text-sm mx-auto mb-1">
              #{c.rank}
            </div>
            <p className="font-semibold text-gray-800 text-sm truncate">{c.name || 'Unknown'}</p>
            <p className="text-xs text-gray-500">{c.experience_years || 0} yrs exp</p>
          </div>
        ))}
      </div>

      {/* Metrics */}
      {metrics.map(m => (
        <div key={m.key} className="grid gap-4 mb-4 items-center"
          style={{ gridTemplateColumns: `140px repeat(${candidates.length}, 1fr)` }}>
          <div className="text-sm text-gray-600 font-medium flex items-center gap-1.5">
            <span>{m.icon}</span> {m.label}
          </div>
          {candidates.map(c => (
            <div key={c.candidate_id} className="text-center">
              <span className="font-bold font-mono text-lg" style={{ color: m.color }}>
                {c[m.key] ?? 0}%
              </span>
              <Bar value={c[m.key]} color={m.color} />
            </div>
          ))}
        </div>
      ))}

      {/* Skills comparison */}
      <div className="grid gap-4 mt-4" style={{ gridTemplateColumns: `140px repeat(${candidates.length}, 1fr)` }}>
        <div className="text-sm text-gray-600 font-medium">🔧 Top Skills</div>
        {candidates.map(c => (
          <div key={c.candidate_id} className="flex flex-wrap gap-1">
            {(c.skills || []).slice(0, 4).map(s => (
              <span key={s} className="text-xs px-1.5 py-0.5 bg-green-100 text-green-800 rounded-full">{s}</span>
            ))}
          </div>
        ))}
      </div>

      {/* EV Level */}
      <div className="grid gap-4 mt-4" style={{ gridTemplateColumns: `140px repeat(${candidates.length}, 1fr)` }}>
        <div className="text-sm text-gray-600 font-medium">⚡ EV Level</div>
        {candidates.map(c => {
          const lvl = c.ev_insights?.ev_experience_level || 'entry';
          return (
            <div key={c.candidate_id} className="text-center">
              <span className={`text-xs px-2 py-1 rounded-full font-semibold ${
                lvl === 'senior' ? 'bg-purple-100 text-purple-700' :
                lvl === 'mid'    ? 'bg-blue-100 text-blue-700' :
                'bg-gray-100 text-gray-600'
              }`}>
                {lvl === 'senior' ? '🏆 Senior' : lvl === 'mid' ? '⚙️ Mid' : '🌱 Entry'}
              </span>
            </div>
          );
        })}
      </div>
    </motion.div>
  );
}
