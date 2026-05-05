import React from 'react';
import { motion } from 'framer-motion';
import jsPDF from 'jspdf';
import toast from 'react-hot-toast';

export default function ShortlistPanel({ candidates }) {
  const exportCSV = () => {
    const rows = [
      ['Rank','Name','Email','Phone','Match%','TF-IDF%','Skill%','Exp%','EV Level','Domains','Skills'],
      ...candidates.map(c => [
        c.rank, c.name, c.email, c.phone,
        c.match_score, c.tfidf_score, c.skill_score, c.exp_score,
        c.ev_insights?.ev_experience_level || '',
        (c.ev_insights?.relevant_domains || []).join('; '),
        (c.skills || []).join('; '),
      ]),
    ];
    const csv = rows.map(r => r.map(v => `"${v ?? ''}"`).join(',')).join('\n');
    const a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([csv], { type: 'text/csv' }));
    a.download = 'ev_shortlisted_candidates.csv';
    a.click();
    toast.success('CSV exported!');
  };

  const exportPDF = () => {
    const doc = new jsPDF();
    doc.setFontSize(18);
    doc.setTextColor(0, 200, 83);
    doc.text('EVisionAstraa — Shortlisted Candidates', 15, 18);
    doc.setFontSize(10);
    doc.setTextColor(0, 0, 0);
    let y = 30;
    candidates.forEach((c, i) => {
      if (y > 270) { doc.addPage(); y = 20; }
      doc.setFontSize(12);
      doc.setTextColor(0, 150, 36);
      doc.text(`${i + 1}. ${c.name || 'Unknown'} — ${c.match_score}% match`, 15, y);
      y += 7;
      doc.setFontSize(9);
      doc.setTextColor(80, 80, 80);
      doc.text(`Email: ${c.email || '—'}  |  Experience: ${c.experience_years || 0} yrs  |  Level: ${c.ev_insights?.ev_experience_level || 'entry'}`, 15, y);
      y += 6;
      doc.text(`Skills: ${(c.skills || []).slice(0, 6).join(', ')}`, 15, y, { maxWidth: 180 });
      y += 10;
    });
    doc.save('ev_shortlisted_candidates.pdf');
    toast.success('PDF exported!');
  };

  if (candidates.length === 0) {
    return (
      <div className="text-center py-16">
        <div className="text-5xl mb-4">⭐</div>
        <h3 className="text-xl font-heading font-semibold text-gray-700 mb-2">No candidates shortlisted yet</h3>
        <p className="text-gray-500">Go to Rankings and click "Shortlist" on candidates you want to keep.</p>
      </div>
    );
  }

  const avg = (candidates.reduce((s, c) => s + c.match_score, 0) / candidates.length).toFixed(1);
  const avgExp = (candidates.reduce((s, c) => s + (c.experience_years || 0), 0) / candidates.length).toFixed(1);

  return (
    <div>
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-xl font-heading font-bold text-gray-800">⭐ Shortlisted Candidates</h2>
          <p className="text-gray-500 text-sm mt-1">{candidates.length} candidate{candidates.length !== 1 ? 's' : ''} selected</p>
        </div>
        <div className="flex gap-2">
          <button onClick={exportCSV} className="btn-outline text-sm px-4 py-2">📊 CSV</button>
          <button onClick={exportPDF} className="btn-primary text-sm px-4 py-2">📥 PDF</button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        {[
          { label: 'Total Shortlisted', value: candidates.length, color: 'text-green-600' },
          { label: 'Avg Match Score',   value: `${avg}%`,         color: 'text-blue-600' },
          { label: 'Avg Experience',    value: `${avgExp} yrs`,   color: 'text-purple-600' },
        ].map((s, i) => (
          <motion.div key={s.label} initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.08 }}
            className="bg-white rounded-2xl p-4 border border-gray-200 shadow-sm">
            <p className="text-xs text-gray-500 mb-1">{s.label}</p>
            <p className={`text-3xl font-bold font-mono ${s.color}`}>{s.value}</p>
          </motion.div>
        ))}
      </div>

      {/* Table */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              {['Rank','Candidate','Match','EV Level','Domains','Top Skills','Contact'].map(h => (
                <th key={h} className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {candidates.map(c => {
              const lvl = c.ev_insights?.ev_experience_level || 'entry';
              const domains = c.ev_insights?.relevant_domains || [];
              return (
                <tr key={c.candidate_id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-4 py-3">
                    <span className="w-8 h-8 rounded-full bg-ev-primary text-white flex items-center justify-center font-bold text-xs">
                      #{c.rank}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <p className="font-semibold text-gray-800">{c.name || 'Unknown'}</p>
                    {c.experience_years > 0 && <p className="text-xs text-gray-500">{c.experience_years} yrs exp</p>}
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <div className="w-12 bg-gray-200 rounded-full h-1.5">
                        <div className="h-1.5 rounded-full bg-ev-primary" style={{ width: `${c.match_score}%` }} />
                      </div>
                      <span className="font-bold font-mono text-ev-primary">{c.match_score}%</span>
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`text-xs px-2 py-1 rounded-full font-semibold ${
                      lvl === 'senior' ? 'bg-purple-100 text-purple-700' :
                      lvl === 'mid'    ? 'bg-blue-100 text-blue-700' :
                      'bg-gray-100 text-gray-600'
                    }`}>
                      {lvl.charAt(0).toUpperCase() + lvl.slice(1)}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex flex-wrap gap-1">
                      {domains.slice(0, 2).map(d => (
                        <span key={d} className="text-xs px-1.5 py-0.5 bg-blue-100 text-blue-700 rounded-full">{d}</span>
                      ))}
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex flex-wrap gap-1">
                      {(c.skills || []).slice(0, 3).map(s => (
                        <span key={s} className="text-xs px-1.5 py-0.5 bg-green-100 text-green-800 rounded-full">{s}</span>
                      ))}
                    </div>
                  </td>
                  <td className="px-4 py-3 text-xs text-gray-500">
                    {c.email && <p className="truncate max-w-[140px]">{c.email}</p>}
                    {c.phone && <p>{c.phone}</p>}
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
