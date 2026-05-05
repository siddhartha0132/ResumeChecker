import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';
import toast from 'react-hot-toast';
import RoleFilter from './RoleFilter';
import CandidateCard from './CandidateCard';
import ResumeViewer from './ResumeViewer';
import ComparisonView from './ComparisonView';
import ShortlistPanel from './ShortlistPanel';
import UploadForm from '../UploadForm';

const VIEWS = ['rankings', 'shortlist', 'upload'];

export default function ManagerDashboard() {
  const [candidates, setCandidates]       = useState([]);
  const [jobSkills, setJobSkills]         = useState([]);
  const [roleFilter, setRoleFilter]       = useState('all');
  const [searchTerm, setSearchTerm]       = useState('');
  const [sortBy, setSortBy]               = useState('rank');
  const [currentView, setCurrentView]     = useState('rankings');
  const [loading, setLoading]             = useState(false);
  const [viewer, setViewer]               = useState(null);
  const [compareMode, setCompareMode]     = useState(false);
  const [compareList, setCompareList]     = useState([]);

  const fetchCandidates = useCallback(async () => {
    try {
      const res = await axios.get('/api/candidates');
      const list = res.data.candidates || [];
      // Add sequential rank if not present
      const ranked = list
        .sort((a, b) => (b.match_score || 0) - (a.match_score || 0))
        .map((c, i) => ({ ...c, rank: i + 1, candidate_id: c.candidate_id ?? c.id ?? i }));
      setCandidates(ranked);
    } catch (e) {
      console.error(e);
    }
  }, []);

  useEffect(() => { fetchCandidates(); }, [fetchCandidates]);

  const handleUploadComplete = (data) => {
    if (data.ranked_candidates) {
      setCandidates(data.ranked_candidates);
      setJobSkills(data.job_skills || []);
      toast.success(`✅ ${data.total_parsed} resumes analyzed!`);
    }
    setCurrentView('rankings');
  };

  const handleShortlist = async (candidateId, status) => {
    const endpoint = status === 'shortlisted' ? 'shortlist' : 'reject';
    try {
      await axios.post(`/api/${endpoint}/${candidateId}`);
      setCandidates(prev => prev.map(c => c.candidate_id === candidateId ? { ...c, status } : c));
      toast.success(status === 'shortlisted' ? '⭐ Shortlisted!' : '❌ Rejected');
    } catch {
      toast.error('Action failed');
    }
  };

  const handleReject = async (candidateId, status) => {
    const endpoint = status === 'rejected' ? 'reject' : 'shortlist';
    try {
      await axios.post(`/api/${endpoint}/${candidateId}`);
      setCandidates(prev => prev.map(c => c.candidate_id === candidateId ? { ...c, status } : c));
    } catch {
      toast.error('Action failed');
    }
  };

  const toggleCompare = (id) => {
    setCompareList(prev =>
      prev.includes(id) ? prev.filter(x => x !== id) : prev.length < 4 ? [...prev, id] : prev
    );
  };

  // Filtered + sorted candidates
  const filtered = candidates
    .filter(c => {
      if (roleFilter !== 'all' && c.role && c.role !== roleFilter) return false;
      if (searchTerm && !c.name?.toLowerCase().includes(searchTerm.toLowerCase())) return false;
      return true;
    })
    .sort((a, b) => {
      if (sortBy === 'score') return (b.match_score || 0) - (a.match_score || 0);
      if (sortBy === 'exp')   return (b.experience_years || 0) - (a.experience_years || 0);
      return (a.rank || 0) - (b.rank || 0);
    });

  const shortlisted = candidates.filter(c => c.status === 'shortlisted');
  const pending     = candidates.filter(c => !c.status || c.status === 'pending');
  const avgScore    = candidates.length
    ? (candidates.reduce((s, c) => s + (c.match_score || 0), 0) / candidates.length).toFixed(1)
    : 0;

  const roleCounts = candidates.reduce((acc, c) => {
    if (c.role) acc[c.role] = (acc[c.role] || 0) + 1;
    return acc;
  }, {});

  const compareCandidates = candidates.filter(c => compareList.includes(c.candidate_id));

  return (
    <div className="min-h-screen bg-ev-bg-light">
      {/* Header */}
      <header className="bg-gradient-to-r from-ev-bg-dark to-gray-800 text-white sticky top-0 z-30 shadow-xl">
        <div className="container mx-auto px-6 py-4 max-w-7xl">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-heading font-bold">HR Manager Dashboard</h1>
              <p className="text-green-300 text-xs mt-0.5">EVisionAstraa Recruitment Portal</p>
            </div>
            <div className="flex gap-4">
              {[
                { label: 'Total',       value: candidates.length },
                { label: 'Shortlisted', value: shortlisted.length },
                { label: 'Pending',     value: pending.length },
                { label: 'Avg Match',   value: `${avgScore}%` },
              ].map(s => (
                <div key={s.label} className="text-center hidden sm:block">
                  <p className="text-xs text-green-300">{s.label}</p>
                  <p className="text-xl font-bold font-mono">{s.value}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-6 max-w-7xl">
        {/* View Tabs */}
        <div className="flex gap-1 mb-6 p-1 bg-white rounded-xl shadow-sm border border-gray-200 w-fit">
          {[
            { key: 'rankings', label: `📊 Rankings (${candidates.length})` },
            { key: 'shortlist', label: `⭐ Shortlist (${shortlisted.length})` },
            { key: 'upload',   label: '📤 Upload Resumes' },
          ].map(tab => (
            <button key={tab.key} onClick={() => setCurrentView(tab.key)}
              className={`px-5 py-2 rounded-lg text-sm font-semibold transition-all duration-200 ${
                currentView === tab.key
                  ? 'bg-ev-primary text-white shadow-md'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* ── Rankings View ── */}
        {currentView === 'rankings' && (
          <>
            {/* Role filter */}
            <RoleFilter selectedRole={roleFilter} onRoleChange={setRoleFilter} counts={roleCounts} />

            {/* Controls */}
            <div className="flex flex-wrap justify-between items-center gap-3 mb-5">
              <div className="flex gap-2 items-center">
                <button
                  onClick={() => { setCompareMode(!compareMode); if (compareMode) setCompareList([]); }}
                  className={`px-4 py-2 rounded-xl text-sm font-semibold transition-all ${
                    compareMode ? 'bg-ev-primary text-white' : 'bg-white border border-gray-200 text-gray-600 hover:border-ev-primary'
                  }`}
                >
                  🔍 Compare {compareList.length > 0 && `(${compareList.length})`}
                </button>
                {compareList.length >= 2 && (
                  <span className="text-xs text-gray-500">Select up to 4 candidates</span>
                )}
              </div>
              <div className="flex gap-2">
                <input
                  type="text" placeholder="Search by name…" value={searchTerm}
                  onChange={e => setSearchTerm(e.target.value)}
                  className="px-3 py-2 text-sm border border-gray-200 rounded-xl bg-white focus:outline-none focus:ring-2 focus:ring-ev-primary/30 w-44"
                />
                <select value={sortBy} onChange={e => setSortBy(e.target.value)}
                  className="px-3 py-2 text-sm border border-gray-200 rounded-xl bg-white focus:outline-none focus:ring-2 focus:ring-ev-primary/30">
                  <option value="rank">Sort: Rank</option>
                  <option value="score">Sort: Score</option>
                  <option value="exp">Sort: Experience</option>
                </select>
              </div>
            </div>

            {/* Comparison view */}
            <AnimatePresence>
              {compareCandidates.length >= 2 && (
                <ComparisonView
                  candidates={compareCandidates}
                  onClose={() => { setCompareList([]); setCompareMode(false); }}
                />
              )}
            </AnimatePresence>

            {/* Job skills reference */}
            {jobSkills.length > 0 && (
              <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 mb-5">
                <p className="text-xs font-semibold text-blue-600 mb-2">
                  🎯 Job Required Skills ({jobSkills.length}) — highlighted in green
                </p>
                <div className="flex flex-wrap gap-1.5">
                  {jobSkills.map(s => (
                    <span key={s} className="text-xs px-2 py-0.5 bg-blue-100 text-blue-700 rounded-full">{s}</span>
                  ))}
                </div>
              </div>
            )}

            {/* Cards */}
            {filtered.length > 0 ? (
              <div className="space-y-4">
                {filtered.map(c => (
                  <CandidateCard
                    key={c.candidate_id}
                    candidate={c}
                    jobSkills={jobSkills}
                    rank={c.rank}
                    onShortlist={handleShortlist}
                    onReject={handleReject}
                    onViewResume={setViewer}
                    compareMode={compareMode}
                    isInCompare={compareList.includes(c.candidate_id)}
                    onToggleCompare={() => toggleCompare(c.candidate_id)}
                  />
                ))}
              </div>
            ) : (
              <div className="text-center py-16 text-gray-400">
                <div className="text-5xl mb-3">🔍</div>
                <p className="text-lg">
                  {candidates.length === 0
                    ? 'No candidates yet — upload resumes in the Upload tab'
                    : 'No candidates match the current filter'}
                </p>
              </div>
            )}
          </>
        )}

        {/* ── Shortlist View ── */}
        {currentView === 'shortlist' && (
          <ShortlistPanel candidates={shortlisted} />
        )}

        {/* ── Upload View ── */}
        {currentView === 'upload' && (
          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}
            className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6 max-w-3xl mx-auto">
            <h2 className="text-xl font-heading font-bold text-gray-800 mb-5">📤 Upload Resumes</h2>
            <UploadForm onUploadComplete={handleUploadComplete} setLoading={setLoading} />
          </motion.div>
        )}
      </main>

      {/* Resume Viewer Modal */}
      <AnimatePresence>
        {viewer && <ResumeViewer candidate={viewer} onClose={() => setViewer(null)} />}
      </AnimatePresence>
    </div>
  );
}
