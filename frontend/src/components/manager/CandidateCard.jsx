import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

function ScoreBadge({ score }) {
  const cls = score >= 70 ? 'score-high' : score >= 45 ? 'score-mid' : 'score-low';
  return (
    <span className={`${cls} px-2.5 py-1 rounded-full text-sm font-bold font-mono`}>
      {score}%
    </span>
  );
}

export default function CandidateCard({
  candidate, jobSkills = [], onShortlist, onReject, onViewResume,
  compareMode, isInCompare, onToggleCompare, rank,
}) {
  const [expanded, setExpanded] = useState(false);

  const {
    candidate_id, name, email, phone, skills = [], experience_years,
    match_score, tfidf_score, skill_score, exp_score,
    status, summary, ev_insights = {}, skill_match = {}, education = [],
  } = candidate;

  const isShortlisted = status === 'shortlisted';
  const isRejected    = status === 'rejected';
  const domains       = ev_insights.relevant_domains || [];
  const level         = ev_insights.ev_experience_level || 'entry';

  const levelBadge = {
    senior: { bg: 'bg-purple-100', text: 'text-purple-700', label: '🏆 Senior' },
    mid:    { bg: 'bg-blue-100',   text: 'text-blue-700',   label: '⚙️ Mid' },
    entry:  { bg: 'bg-gray-100',   text: 'text-gray-600',   label: '🌱 Entry' },
  }[level];

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      className={`bg-white rounded-2xl border-l-4 shadow-sm hover:shadow-md transition-all duration-200 overflow-hidden ${
        isShortlisted ? 'border-l-green-500' :
        isRejected    ? 'border-l-red-400 opacity-60' :
        'border-l-gray-200'
      }`}
    >
      <div className="p-5">
        {/* Top row */}
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-center gap-3 min-w-0">
            {/* Compare checkbox */}
            {compareMode && (
              <input type="checkbox" checked={isInCompare} onChange={onToggleCompare}
                className="w-4 h-4 accent-ev-primary flex-shrink-0" />
            )}
            {/* Rank */}
            <div className="w-9 h-9 rounded-full bg-ev-primary text-white flex items-center justify-center font-bold text-sm flex-shrink-0">
              #{rank}
            </div>
            <div className="min-w-0">
              <h3 className="font-heading font-bold text-gray-800 truncate">{name || 'Unknown'}</h3>
              <div className="flex flex-wrap gap-2 text-xs text-gray-500 mt-0.5">
                {email && <span>✉️ {email}</span>}
                {phone && <span>📞 {phone}</span>}
                {experience_years > 0 && <span>🗓 {experience_years} yrs</span>}
              </div>
            </div>
          </div>

          <div className="flex flex-col items-end gap-1.5 flex-shrink-0">
            {/* Score with tooltip */}
            <div className="group relative">
              <ScoreBadge score={match_score} />
              <div className="absolute bottom-full right-0 mb-2 w-52 p-3 bg-gray-900 rounded-xl text-xs
                opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-50 shadow-xl">
                <p className="text-green-400 font-bold mb-2">Score Breakdown</p>
                {[
                  { l: 'Text Relevance (50%)', v: tfidf_score,  c: '#60a5fa' },
                  { l: 'Skill Match (30%)',    v: skill_score,  c: '#00ff88' },
                  { l: 'Experience (20%)',     v: exp_score,    c: '#c084fc' },
                ].map(r => (
                  <div key={r.l} className="mb-1.5">
                    <div className="flex justify-between mb-0.5">
                      <span className="text-gray-400">{r.l}</span>
                      <span className="font-mono font-bold" style={{ color: r.c }}>{r.v ?? 0}%</span>
                    </div>
                    <div className="w-full bg-gray-700 rounded-full h-1">
                      <div className="h-1 rounded-full" style={{ width: `${r.v ?? 0}%`, background: r.c }} />
                    </div>
                  </div>
                ))}
              </div>
            </div>
            <span className={`text-xs px-2 py-0.5 rounded-full font-semibold ${levelBadge.bg} ${levelBadge.text}`}>
              {levelBadge.label}
            </span>
          </div>
        </div>

        {/* Domains */}
        {domains.length > 0 && (
          <div className="flex flex-wrap gap-1.5 mt-3">
            {domains.map(d => (
              <span key={d} className="text-xs px-2 py-0.5 bg-blue-50 text-blue-700 rounded-full border border-blue-100">{d}</span>
            ))}
          </div>
        )}

        {/* Skills */}
        {skills.length > 0 && (
          <div className="flex flex-wrap gap-1.5 mt-3">
            {skills.slice(0, expanded ? skills.length : 5).map(s => {
              const matched = jobSkills.map(j => j.toLowerCase()).includes(s.toLowerCase());
              return (
                <span key={s} className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                  matched ? 'bg-green-100 text-green-800 ring-1 ring-green-300' : 'bg-gray-100 text-gray-600'
                }`}>{s}</span>
              );
            })}
            {!expanded && skills.length > 5 && (
              <button onClick={() => setExpanded(true)} className="text-xs text-blue-500 hover:underline">
                +{skills.length - 5} more
              </button>
            )}
          </div>
        )}

        {/* Skill match bar */}
        {skill_match.match_percent !== undefined && (
          <div className="mt-3 bg-gray-50 rounded-xl p-3">
            <div className="flex justify-between text-xs mb-1">
              <span className="text-gray-500">Skill Match</span>
              <span className="font-bold text-gray-700">{skill_match.match_percent}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-1.5">
              <div className="h-1.5 rounded-full bg-ev-primary transition-all duration-700"
                style={{ width: `${skill_match.match_percent}%` }} />
            </div>
            {skill_match.matching_skills?.length > 0 && (
              <p className="text-xs text-green-600 mt-1">
                ✅ {skill_match.matching_skills.slice(0, 3).join(', ')}
                {skill_match.matching_skills.length > 3 && ` +${skill_match.matching_skills.length - 3}`}
              </p>
            )}
          </div>
        )}

        {/* Expanded: summary + education */}
        <AnimatePresence>
          {expanded && (
            <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} exit={{ opacity: 0, height: 0 }}>
              {summary && (
                <div className="mt-3 bg-blue-50 rounded-xl p-3 border border-blue-100">
                  <p className="text-xs font-semibold text-blue-600 mb-1">🤖 AI Summary</p>
                  <p className="text-sm text-gray-600">{summary}</p>
                </div>
              )}
              {education.length > 0 && (
                <div className="mt-3">
                  {education.map((e, i) => <p key={i} className="text-xs text-gray-500">🎓 {e}</p>)}
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Actions */}
        <div className="flex justify-between items-center mt-4 pt-3 border-t border-gray-100">
          <button onClick={() => setExpanded(!expanded)} className="text-xs text-blue-500 hover:underline">
            {expanded ? '▲ Less' : '▼ More'}
          </button>
          <div className="flex gap-2">
            <button onClick={() => onViewResume(candidate)}
              className="px-3 py-1.5 text-xs bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition">
              👁 View
            </button>
            {!isRejected && (
              <button
                onClick={() => onShortlist(candidate_id, isShortlisted ? 'pending' : 'shortlisted')}
                className={`px-3 py-1.5 text-xs rounded-lg transition font-semibold ${
                  isShortlisted
                    ? 'bg-green-100 text-green-700 hover:bg-green-200'
                    : 'bg-gray-100 text-gray-600 hover:bg-green-100 hover:text-green-700'
                }`}
              >
                {isShortlisted ? '⭐ Shortlisted' : '☆ Shortlist'}
              </button>
            )}
            {!isShortlisted && (
              <button
                onClick={() => onReject(candidate_id, isRejected ? 'pending' : 'rejected')}
                className={`px-3 py-1.5 text-xs rounded-lg transition ${
                  isRejected ? 'bg-red-100 text-red-600' : 'bg-gray-100 text-gray-500 hover:bg-red-100 hover:text-red-600'
                }`}
              >
                {isRejected ? '✗ Rejected' : '✗ Reject'}
              </button>
            )}
          </div>
        </div>
      </div>
    </motion.div>
  );
}
