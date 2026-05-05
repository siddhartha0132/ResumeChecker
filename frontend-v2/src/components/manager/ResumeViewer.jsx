import React from 'react';
import { motion } from 'framer-motion';

export default function ResumeViewer({ candidate, onClose }) {
  const {
    name, email, phone, skills = [], experience_years,
    match_score, tfidf_score, skill_score, exp_score,
    summary, ev_insights = {}, skill_match = {}, education = [],
    text_preview = '',
  } = candidate;

  const domains = ev_insights.relevant_domains || [];
  const level   = ev_insights.ev_experience_level || 'entry';

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      style={{ background: 'rgba(0,0,0,0.6)', backdropFilter: 'blur(4px)' }}
      onClick={onClose}
    >
      <motion.div
        initial={{ scale: 0.92, y: 20 }}
        animate={{ scale: 1, y: 0 }}
        exit={{ scale: 0.92 }}
        onClick={e => e.stopPropagation()}
        className="bg-white rounded-3xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto"
      >
        {/* Header */}
        <div className="sticky top-0 bg-white border-b border-gray-100 px-6 py-4 flex justify-between items-center rounded-t-3xl">
          <div>
            <h2 className="text-xl font-heading font-bold text-gray-800">{name || 'Candidate'}</h2>
            <p className="text-sm text-gray-500">{email}</p>
          </div>
          <button onClick={onClose} className="w-8 h-8 rounded-full bg-gray-100 hover:bg-gray-200 flex items-center justify-center text-gray-600 transition">
            ✕
          </button>
        </div>

        <div className="p-6 space-y-5">
          {/* Score overview */}
          <div className="grid grid-cols-4 gap-3">
            {[
              { label: 'Overall',    value: match_score, color: '#00C853' },
              { label: 'Relevance', value: tfidf_score,  color: '#2979FF' },
              { label: 'Skills',    value: skill_score,  color: '#00C853' },
              { label: 'Experience',value: exp_score,    color: '#c084fc' },
            ].map(s => (
              <div key={s.label} className="bg-gray-50 rounded-xl p-3 text-center border border-gray-100">
                <p className="text-xs text-gray-500 mb-1">{s.label}</p>
                <p className="text-xl font-bold font-mono" style={{ color: s.color }}>{s.value ?? 0}%</p>
              </div>
            ))}
          </div>

          {/* Info */}
          <div className="flex flex-wrap gap-2">
            {phone && <span className="text-sm text-gray-600 bg-gray-100 px-3 py-1 rounded-full">📞 {phone}</span>}
            {experience_years > 0 && <span className="text-sm text-gray-600 bg-gray-100 px-3 py-1 rounded-full">🗓 {experience_years} yrs exp</span>}
            <span className="text-sm bg-purple-100 text-purple-700 px-3 py-1 rounded-full">
              {level === 'senior' ? '🏆 Senior' : level === 'mid' ? '⚙️ Mid-Level' : '🌱 Entry'}
            </span>
          </div>

          {/* Domains */}
          {domains.length > 0 && (
            <div>
              <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">EV Domains</p>
              <div className="flex flex-wrap gap-2">
                {domains.map(d => <span key={d} className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm">{d}</span>)}
              </div>
            </div>
          )}

          {/* Skills */}
          {skills.length > 0 && (
            <div>
              <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Skills ({skills.length})</p>
              <div className="flex flex-wrap gap-1.5">
                {skills.map(s => (
                  <span key={s} className="px-2.5 py-1 bg-green-100 text-green-800 rounded-full text-xs font-medium">{s}</span>
                ))}
              </div>
            </div>
          )}

          {/* Skill gap */}
          {(skill_match.matching_skills?.length > 0 || skill_match.missing_skills?.length > 0) && (
            <div className="bg-gray-50 rounded-2xl p-4 border border-gray-100">
              <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">Skill Gap Analysis</p>
              <div className="flex justify-between text-sm mb-2">
                <span className="text-gray-600">Match Rate</span>
                <span className="font-bold text-ev-primary">{skill_match.match_percent}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2 mb-3">
                <div className="h-2 rounded-full bg-ev-primary" style={{ width: `${skill_match.match_percent}%` }} />
              </div>
              {skill_match.missing_skills?.length > 0 && (
                <div>
                  <p className="text-xs text-red-500 font-semibold mb-1.5">Missing Skills</p>
                  <div className="flex flex-wrap gap-1.5">
                    {skill_match.missing_skills.map(s => (
                      <span key={s} className="px-2 py-0.5 bg-red-100 text-red-700 rounded-full text-xs">{s}</span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Education */}
          {education.length > 0 && (
            <div>
              <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Education</p>
              {education.map((e, i) => <p key={i} className="text-sm text-gray-600">🎓 {e}</p>)}
            </div>
          )}

          {/* AI Summary */}
          {summary && (
            <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-2xl p-4 border border-green-100">
              <p className="text-xs font-semibold text-gray-600 mb-2">🤖 AI Summary</p>
              <p className="text-sm text-gray-700 leading-relaxed">{summary}</p>
            </div>
          )}

          {/* Raw text preview */}
          {text_preview && (
            <div>
              <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Resume Text Preview</p>
              <pre className="text-xs text-gray-500 bg-gray-50 rounded-xl p-4 overflow-auto max-h-48 font-mono whitespace-pre-wrap border border-gray-100">
                {text_preview.slice(0, 800)}…
              </pre>
            </div>
          )}
        </div>
      </motion.div>
    </motion.div>
  );
}
