import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { CircularProgressbar, buildStyles } from 'react-circular-progressbar';
import 'react-circular-progressbar/dist/styles.css';
import jsPDF from 'jspdf';
import toast from 'react-hot-toast';

function scoreColor(s) {
  if (s >= 75) return '#00C853';
  if (s >= 50) return '#FFD600';
  return '#FF5252';
}
function scoreLabel(s) {
  if (s >= 75) return { text: 'Excellent Match! 🎉', cls: 'text-green-600' };
  if (s >= 55) return { text: 'Good Match 👍',       cls: 'text-yellow-600' };
  if (s >= 35) return { text: 'Potential Match 📈',  cls: 'text-orange-500' };
  return              { text: 'Needs Improvement 📚', cls: 'text-red-500' };
}

export default function ScoreDisplay({ data, selectedRole, onRestart }) {
  const {
    score = 0, tfidf = 0, skillPct = 0, expPct = 0,
    skills = [], skillMatch = {}, summary = '', evInsights = {}, name = '', jobSkills = [],
  } = data;

  const [showAll, setShowAll] = useState(false);
  const lbl = scoreLabel(score);

  const breakdown = [
    { icon: '📄', label: 'Text Relevance',  score: tfidf,    weight: '50%', color: '#2979FF' },
    { icon: '🔧', label: 'Skill Match',     score: skillPct, weight: '30%', color: '#00C853' },
    { icon: '📅', label: 'Experience',      score: expPct,   weight: '20%', color: '#c084fc' },
  ];

  const domains = evInsights.relevant_domains || [];
  const level   = evInsights.ev_experience_level || 'entry';
  const matching = skillMatch.matching_skills || [];
  const missing  = skillMatch.missing_skills  || [];

  const exportPDF = () => {
    const doc = new jsPDF();
    doc.setFontSize(20);
    doc.setTextColor(0, 200, 83);
    doc.text('EVisionAstraa — Application Report', 20, 20);
    doc.setFontSize(12);
    doc.setTextColor(0, 0, 0);
    doc.text(`Candidate: ${name || 'Applicant'}`, 20, 35);
    doc.text(`Role: ${selectedRole?.title || ''}`, 20, 45);
    doc.text(`Overall Match Score: ${score}%`, 20, 55);
    doc.text(`Text Relevance: ${tfidf}%`, 20, 65);
    doc.text(`Skill Match: ${skillPct}%`, 20, 75);
    doc.text(`Experience Score: ${expPct}%`, 20, 85);
    doc.text(`EV Level: ${level}`, 20, 95);
    doc.text(`Domains: ${domains.join(', ')}`, 20, 105);
    doc.text(`Matched Skills: ${matching.join(', ')}`, 20, 115, { maxWidth: 170 });
    doc.text(`Missing Skills: ${missing.join(', ')}`, 20, 130, { maxWidth: 170 });
    if (summary) {
      doc.text('AI Summary:', 20, 145);
      doc.setFontSize(10);
      doc.text(summary, 20, 153, { maxWidth: 170 });
    }
    doc.save(`${name || 'candidate'}_ev_report.pdf`);
    toast.success('PDF report downloaded!');
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-3xl shadow-2xl p-8 max-w-3xl mx-auto"
    >
      <h3 className="text-3xl font-heading font-bold text-center text-gray-800 mb-2">
        Your Application Results
      </h3>
      {name && <p className="text-center text-gray-500 mb-6">Hi <strong>{name}</strong> 👋</p>}

      {/* Circular score */}
      <div className="flex justify-center mb-6">
        <div className="w-44 h-44">
          <CircularProgressbar
            value={score}
            text={`${score}%`}
            styles={buildStyles({
              textSize: '22px',
              pathColor: scoreColor(score),
              textColor: scoreColor(score),
              trailColor: '#E5E7EB',
              pathTransitionDuration: 1.2,
            })}
          />
        </div>
      </div>

      <p className={`text-center text-2xl font-bold mb-6 ${lbl.cls}`}>{lbl.text}</p>

      {/* Breakdown */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        {breakdown.map((b, i) => (
          <motion.div
            key={b.label}
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 + i * 0.1 }}
            className="bg-gray-50 rounded-2xl p-4 text-center border border-gray-100"
          >
            <div className="text-2xl mb-1">{b.icon}</div>
            <p className="text-xs text-gray-500 mb-1">{b.label} <span className="text-gray-400">({b.weight})</span></p>
            <p className="text-2xl font-bold font-mono" style={{ color: b.color }}>{b.score}%</p>
            <div className="w-full bg-gray-200 rounded-full h-1.5 mt-2">
              <motion.div
                className="h-1.5 rounded-full"
                style={{ background: b.color }}
                initial={{ width: 0 }}
                animate={{ width: `${b.score}%` }}
                transition={{ delay: 0.4 + i * 0.1, duration: 0.8 }}
              />
            </div>
          </motion.div>
        ))}
      </div>

      {/* EV Level + Domains */}
      <div className="flex flex-wrap gap-2 justify-center mb-5">
        <span className="px-3 py-1 rounded-full text-sm font-semibold bg-purple-100 text-purple-700">
          {level === 'senior' ? '🏆 Senior' : level === 'mid' ? '⚙️ Mid-Level' : '🌱 Entry'} EV Engineer
        </span>
        {domains.map(d => (
          <span key={d} className="px-3 py-1 rounded-full text-sm bg-blue-100 text-blue-700">{d}</span>
        ))}
      </div>

      {/* Skill match */}
      {(matching.length > 0 || missing.length > 0) && (
        <div className="bg-gray-50 rounded-2xl p-5 mb-5 border border-gray-100">
          <h4 className="font-semibold text-gray-700 mb-3">Skill Gap Analysis</h4>
          {matching.length > 0 && (
            <div className="mb-2">
              <p className="text-xs text-green-600 font-semibold mb-1.5">✅ Matched ({matching.length})</p>
              <div className="flex flex-wrap gap-1.5">
                {matching.map(s => (
                  <span key={s} className="px-2 py-0.5 bg-green-100 text-green-800 rounded-full text-xs">{s}</span>
                ))}
              </div>
            </div>
          )}
          {missing.length > 0 && (
            <div>
              <p className="text-xs text-red-500 font-semibold mb-1.5">❌ Missing ({missing.length})</p>
              <div className="flex flex-wrap gap-1.5">
                {(showAll ? missing : missing.slice(0, 5)).map(s => (
                  <span key={s} className="px-2 py-0.5 bg-red-100 text-red-700 rounded-full text-xs">{s}</span>
                ))}
                {missing.length > 5 && (
                  <button onClick={() => setShowAll(!showAll)} className="text-xs text-blue-500 hover:underline">
                    {showAll ? 'Show less' : `+${missing.length - 5} more`}
                  </button>
                )}
              </div>
            </div>
          )}
        </div>
      )}

      {/* AI Summary */}
      {summary && (
        <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-2xl p-5 mb-6 border border-green-100">
          <h4 className="font-semibold text-gray-700 mb-2 flex items-center gap-2">
            <span>🤖</span> AI Resume Summary
          </h4>
          <p className="text-gray-600 text-sm leading-relaxed">{summary}</p>
        </div>
      )}

      {/* Actions */}
      <div className="flex gap-3">
        <button onClick={onRestart} className="btn-outline flex-1">
          ← Apply for Another Role
        </button>
        <button onClick={exportPDF} className="btn-primary flex-1">
          📥 Download PDF Report
        </button>
      </div>
    </motion.div>
  );
}
