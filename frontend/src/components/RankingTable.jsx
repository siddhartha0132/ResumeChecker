import React, { useState } from 'react';
import { motion } from 'framer-motion';
import CandidateCard from './CandidateCard';

export default function RankingTable({ candidates, jobSkills, onShortlist }) {
  const [filter, setFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState('rank');

  const filtered = candidates
    .filter(c => {
      if (filter === 'shortlisted' && c.status !== 'shortlisted') return false;
      if (filter === 'pending' && (c.status === 'shortlisted' || c.status === 'rejected')) return false;
      if (filter === 'rejected' && c.status !== 'rejected') return false;
      if (searchTerm && !c.name?.toLowerCase().includes(searchTerm.toLowerCase())) return false;
      return true;
    })
    .sort((a, b) => {
      if (sortBy === 'score') return b.match_score - a.match_score;
      if (sortBy === 'experience') return (b.experience_years || 0) - (a.experience_years || 0);
      return a.rank - b.rank;
    });

  const total        = candidates.length;
  const avgScore     = total > 0 ? (candidates.reduce((s, c) => s + c.match_score, 0) / total).toFixed(1) : 0;
  const topScore     = total > 0 ? Math.max(...candidates.map(c => c.match_score)) : 0;
  const shortlisted  = candidates.filter(c => c.status === 'shortlisted').length;
  const highMatches  = candidates.filter(c => c.match_score >= 80).length;

  const stats = [
    { label: 'Avg Match', value: `${avgScore}%`, gradient: 'from-blue-600 to-blue-500' },
    { label: 'Top Score', value: `${topScore}%`, gradient: 'from-green-600 to-green-500' },
    { label: 'Shortlisted', value: shortlisted, gradient: 'from-purple-600 to-purple-500' },
    { label: '80%+ Matches', value: highMatches, gradient: 'from-orange-600 to-orange-500' },
  ];

  const filterBtns = [
    { key: 'all', label: `All (${total})` },
    { key: 'pending', label: `Pending (${candidates.filter(c => !c.status || c.status === 'pending').length})` },
    { key: 'shortlisted', label: `Shortlisted (${shortlisted})` },
    { key: 'rejected', label: `Rejected (${candidates.filter(c => c.status === 'rejected').length})` },
  ];

  return (
    <div>
      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        {stats.map((s, i) => (
          <motion.div
            key={s.label}
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.07 }}
            className={`bg-gradient-to-br ${s.gradient} rounded-xl p-4 shadow-lg`}
          >
            <p className="text-xs text-white/70 mb-1">{s.label}</p>
            <p className="text-2xl font-bold text-white tabular-nums">{s.value}</p>
          </motion.div>
        ))}
      </div>

      {/* Filters + Search */}
      <div className="flex flex-wrap justify-between items-center gap-3 mb-5">
        <div className="flex flex-wrap gap-2">
          {filterBtns.map(btn => (
            <button
              key={btn.key}
              onClick={() => setFilter(btn.key)}
              className="px-3 py-1.5 rounded-lg text-sm font-semibold transition-all duration-200"
              style={filter === btn.key
                ? { background: '#00C853', color: '#000', boxShadow: '0 0 12px rgba(0,200,83,0.3)' }
                : { background: 'rgba(255,255,255,0.06)', color: '#9ca3af', border: '1px solid rgba(255,255,255,0.08)' }
              }
            >
              {btn.label}
            </button>
          ))}
        </div>

        <div className="flex gap-2">
          <input
            type="text"
            placeholder="Search by name…"
            value={searchTerm}
            onChange={e => setSearchTerm(e.target.value)}
            className="px-3 py-1.5 text-sm w-44"
            style={{ background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '10px', color: 'white' }}
          />
          <select
            value={sortBy}
            onChange={e => setSortBy(e.target.value)}
            className="px-3 py-1.5 text-sm"
            style={{ background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '10px', color: 'white' }}
          >
            <option value="rank" style={{ background: '#0a0a0a' }}>Sort: Rank</option>
            <option value="score" style={{ background: '#0a0a0a' }}>Sort: Score</option>
            <option value="experience" style={{ background: '#0a0a0a' }}>Sort: Experience</option>
          </select>
        </div>
      </div>

      {/* Job Skills Reference */}
      {jobSkills.length > 0 && (
        <div className="rounded-xl p-4 mb-5" style={{ background: 'rgba(0,145,234,0.08)', border: '1px solid rgba(0,145,234,0.2)' }}>
          <p className="text-xs font-semibold text-blue-400 mb-2">
            🎯 Job Required Skills ({jobSkills.length}) — highlighted in green on each candidate
          </p>
          <div className="flex flex-wrap gap-1.5">
            {jobSkills.map(skill => (
              <span
                key={skill}
                className="text-xs px-2 py-0.5 rounded-full"
                style={{ background: 'rgba(0,145,234,0.15)', color: '#60a5fa', border: '1px solid rgba(0,145,234,0.25)' }}
              >
                {skill}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Cards */}
      {filtered.length > 0 ? (
        <div className="space-y-4">
          {filtered.map(candidate => (
            <CandidateCard
              key={candidate.candidate_id}
              candidate={candidate}
              jobSkills={jobSkills}
              onShortlist={onShortlist}
            />
          ))}
        </div>
      ) : (
        <div className="text-center py-14 text-gray-500">
          <div className="text-4xl mb-3">🔍</div>
          <p>No candidates match the current filter.</p>
        </div>
      )}
    </div>
  );
}
