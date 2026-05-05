import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const LEVEL_STYLES = {
  senior: { bg: 'rgba(168,85,247,0.15)', color: '#c084fc', border: 'rgba(168,85,247,0.3)', label: '🏆 Senior' },
  mid:    { bg: 'rgba(59,130,246,0.15)', color: '#60a5fa', border: 'rgba(59,130,246,0.3)', label: '⚙️ Mid-Level' },
  entry:  { bg: 'rgba(156,163,175,0.1)', color: '#9ca3af', border: 'rgba(156,163,175,0.2)', label: '🌱 Entry' },
};

function MatchBadge({ score, tfidf, skillScore, expScore }) {
  const cls = score >= 70 ? 'match-high' : score >= 45 ? 'match-mid' : 'match-low';
  return (
    <div className="group relative">
      <span className={`${cls} px-2.5 py-1 rounded-full text-xs font-bold tabular-nums cursor-help`}>
        {score}% Match
      </span>
      {/* Tooltip */}
      <div className="absolute bottom-full right-0 mb-2 w-52 p-3 rounded-xl text-xs opacity-0 group-hover:opacity-100 transition-all duration-200 pointer-events-none z-50"
        style={{ background: 'rgba(0,0,0,0.92)', border: '1px solid rgba(0,200,83,0.3)', backdropFilter: 'blur(8px)' }}>
        <p className="font-bold text-green-400 mb-2">Score Breakdown</p>
        <div className="space-y-1.5">
          <ScoreRow label="Text Relevance (50%)" value={tfidf} color="#60a5fa" />
          <ScoreRow label="Skill Match (30%)"    value={skillScore} color="#00ff88" />
          <ScoreRow label="Experience (20%)"     value={expScore} color="#c084fc" />
        </div>
      </div>
    </div>
  );
}

function ScoreRow({ label, value, color }) {
  return (
    <div>
      <div className="flex justify-between mb-0.5">
        <span className="text-gray-400">{label}</span>
        <span className="font-semibold tabular-nums" style={{ color }}>{value ?? '—'}%</span>
      </div>
      <div className="w-full rounded-full h-1" style={{ background: 'rgba(255,255,255,0.08)' }}>
        <div className="h-1 rounded-full" style={{ width: `${value ?? 0}%`, background: color }} />
      </div>
    </div>
  );
}

export default function CandidateCard({ candidate, jobSkills = [], onShortlist }) {
  const [expanded, setExpanded] = useState(false);

  const {
    candidate_id, rank, name, email, phone,
    skills = [], experience_years, education = [],
    match_score, tfidf_score, skill_score, exp_score,
    status, summary, ev_insights = {}, skill_match = {},
  } = candidate;

  const isShortlisted = status === 'shortlisted';
  const isRejected    = status === 'rejected';
  const evLevel       = ev_insights.ev_experience_level || 'entry';
  const domains       = ev_insights.relevant_domains || [];
  const lvl           = LEVEL_STYLES[evLevel];

  const borderColor = isShortlisted ? '#00ff88' : isRejected ? '#ff6644' : 'rgba(255,255,255,0.08)';

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-card rounded-2xl p-5"
      style={{
        borderLeft: `4px solid ${borderColor}`,
        opacity: isRejected ? 0.55 : 1,
      }}
    >
      {/* Top Row */}
      <div className="flex justify-between items-start gap-4">
        <div className="flex items-center gap-3 min-w-0">
          {/* Rank badge */}
          <div
            className="flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center font-bold text-sm text-black"
            style={{ background: 'linear-gradient(135deg, #00C853, #00ff88)' }}
          >
            #{rank}
          </div>

          <div className="min-w-0">
            <h3 className="font-bold text-white text-base truncate">
              {name || 'Unknown Candidate'}
            </h3>
            <div className="flex flex-wrap gap-3 mt-0.5 text-xs text-gray-500">
              {email && <span>✉️ {email}</span>}
              {phone && <span>📞 {phone}</span>}
              {experience_years > 0 && <span>🗓 {experience_years} yrs</span>}
            </div>
          </div>
        </div>

        <div className="flex flex-col items-end gap-1.5 flex-shrink-0">
          <MatchBadge score={match_score} tfidf={tfidf_score} skillScore={skill_score} expScore={exp_score} />
          <span
            className="text-xs px-2 py-0.5 rounded-full font-semibold"
            style={{ background: lvl.bg, color: lvl.color, border: `1px solid ${lvl.border}` }}
          >
            {lvl.label}
          </span>
        </div>
      </div>

      {/* EV Domains */}
      {domains.length > 0 && (
        <div className="flex flex-wrap gap-1.5 mt-3">
          {domains.map(domain => (
            <span
              key={domain}
              className="text-xs px-2 py-0.5 rounded-full font-medium"
              style={{ background: 'rgba(0,145,234,0.12)', color: '#60a5fa', border: '1px solid rgba(0,145,234,0.25)' }}
            >
              {domain}
            </span>
          ))}
        </div>
      )}

      {/* Skills */}
      {skills.length > 0 && (
        <div className="mt-3 flex flex-wrap gap-1.5">
          {skills.slice(0, expanded ? skills.length : 6).map(skill => {
            const isMatch = jobSkills.map(s => s.toLowerCase()).includes(skill.toLowerCase());
            return (
              <span
                key={skill}
                className="text-xs px-2 py-0.5 rounded-full font-medium"
                style={isMatch
                  ? { background: 'rgba(0,200,83,0.15)', color: '#00ff88', border: '1px solid rgba(0,200,83,0.35)' }
                  : { background: 'rgba(255,255,255,0.06)', color: '#9ca3af', border: '1px solid rgba(255,255,255,0.08)' }
                }
              >
                {skill}
              </span>
            );
          })}
          {!expanded && skills.length > 6 && (
            <button onClick={() => setExpanded(true)} className="text-xs text-blue-400 hover:underline">
              +{skills.length - 6} more
            </button>
          )}
        </div>
      )}

      {/* Skill Match Bar */}
      {skill_match.match_percent !== undefined && (
        <div className="mt-3 rounded-xl p-3" style={{ background: 'rgba(0,0,0,0.3)' }}>
          <div className="flex justify-between text-xs mb-1.5">
            <span className="text-gray-500">Skill Match</span>
            <span className="font-semibold text-white">{skill_match.match_percent}%</span>
          </div>
          <div className="w-full rounded-full h-1.5" style={{ background: 'rgba(255,255,255,0.08)' }}>
            <div
              className="h-1.5 rounded-full transition-all duration-700"
              style={{
                width: `${skill_match.match_percent}%`,
                background: 'linear-gradient(90deg, #00C853, #00ff88)',
              }}
            />
          </div>
          {skill_match.matching_skills?.length > 0 && (
            <p className="text-xs mt-1.5" style={{ color: '#00ff88' }}>
              ✅ {skill_match.matching_skills.slice(0, 3).join(', ')}
              {skill_match.matching_skills.length > 3 && ` +${skill_match.matching_skills.length - 3} more`}
            </p>
          )}
          {skill_match.missing_skills?.length > 0 && (
            <p className="text-xs mt-0.5 text-red-400">
              ❌ Missing: {skill_match.missing_skills.slice(0, 3).join(', ')}
              {skill_match.missing_skills.length > 3 && ` +${skill_match.missing_skills.length - 3} more`}
            </p>
          )}
        </div>
      )}

      {/* Expanded: Summary */}
      <AnimatePresence>
        {expanded && summary && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="mt-3 rounded-xl p-3"
            style={{ background: 'rgba(0,145,234,0.08)', border: '1px solid rgba(0,145,234,0.15)' }}
          >
            <p className="text-xs font-semibold text-blue-400 mb-1">AI Summary</p>
            <p className="text-sm text-gray-300">{summary}</p>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Expanded: Education */}
      <AnimatePresence>
        {expanded && education.length > 0 && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="mt-3"
          >
            <p className="text-xs font-semibold text-gray-500 mb-1">Education</p>
            {education.map((edu, i) => (
              <p key={i} className="text-sm text-gray-400">🎓 {edu}</p>
            ))}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Actions */}
      <div className="flex justify-between items-center mt-4 pt-3" style={{ borderTop: '1px solid rgba(255,255,255,0.06)' }}>
        <button
          onClick={() => setExpanded(!expanded)}
          className="text-xs text-blue-400 hover:text-blue-300 transition-colors"
        >
          {expanded ? '▲ Show less' : '▼ Show more'}
        </button>

        <div className="flex gap-2">
          {!isRejected && (
            <button
              onClick={() => onShortlist(candidate_id, isShortlisted ? 'pending' : 'shortlisted')}
              className="px-3 py-1.5 rounded-lg text-xs font-semibold transition-all duration-200"
              style={isShortlisted
                ? { background: 'rgba(0,200,83,0.2)', color: '#00ff88', border: '1px solid rgba(0,200,83,0.4)' }
                : { background: 'rgba(255,255,255,0.06)', color: '#9ca3af', border: '1px solid rgba(255,255,255,0.1)' }
              }
            >
              {isShortlisted ? '⭐ Shortlisted' : '☆ Shortlist'}
            </button>
          )}
          {!isShortlisted && (
            <button
              onClick={() => onShortlist(candidate_id, isRejected ? 'pending' : 'rejected')}
              className="px-3 py-1.5 rounded-lg text-xs font-semibold transition-all duration-200"
              style={isRejected
                ? { background: 'rgba(255,80,60,0.2)', color: '#ff6644', border: '1px solid rgba(255,80,60,0.4)' }
                : { background: 'rgba(255,255,255,0.06)', color: '#9ca3af', border: '1px solid rgba(255,255,255,0.1)' }
              }
            >
              {isRejected ? '✗ Rejected' : '✗ Reject'}
            </button>
          )}
        </div>
      </div>
    </motion.div>
  );
}
