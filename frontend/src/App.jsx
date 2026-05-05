import React, { useState, Suspense, lazy } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import ParticleBackground from './components/ParticleBackground';
import RotatingEVLogo3D from './components/RotatingEVLogo3D';
import EVScooter3D from './components/EVScooter3D';
import FloatingCards3D from './components/FloatingCard3D';
import UploadForm from './components/UploadForm';
import toast, { Toaster } from 'react-hot-toast';

// Lazy load heavy table components
const RankingTable = lazy(() => import('./components/RankingTable'));
const ShortlistPanel = lazy(() => import('./components/ShortlistPanel'));

function App() {
  const [rankedCandidates, setRankedCandidates] = useState([]);
  const [loading, setLoading] = useState(false);
  const [jobSkills, setJobSkills] = useState([]);
  const [currentView, setCurrentView] = useState('ranking');
  const [hoveredCandidate, setHoveredCandidate] = useState(null);

  const handleUploadComplete = (data) => {
    console.log('handleUploadComplete called with:', data);
    if (data.ranked_candidates) {
      setRankedCandidates(data.ranked_candidates);
      setJobSkills(data.job_skills || []);
      toast.success(`✅ ${data.total_parsed} candidates analyzed!`);
    } else if (data.candidates) {
      // No job description was provided — still show candidates
      setRankedCandidates(data.candidates.map((c, i) => ({ ...c, rank: i + 1, match_score: 0, candidate_id: i })));
      toast.success(`✅ ${data.total_parsed} resumes parsed (no ranking — add a job description)`);
    } else {
      toast.error('No candidates were parsed. Check that the PDFs contain readable text.');
    }
    setCurrentView('ranking');
  };

  const handleShortlistToggle = (candidateId, status) => {
    setRankedCandidates(prev =>
      prev.map(c => c.candidate_id === candidateId ? { ...c, status } : c)
    );
    toast.success(status === 'shortlisted' ? '⭐ Candidate shortlisted!' : '❌ Candidate rejected');
  };

  const shortlistedCount = rankedCandidates.filter(c => c.status === 'shortlisted').length;
  const pendingCount = rankedCandidates.filter(c => !c.status || c.status === 'pending').length;

  return (
    <div className="min-h-screen relative text-white">
      {/* 3D Particle Background */}
      <ParticleBackground />

      {/* Main Content */}
      <div className="relative z-10">
        <Toaster
          position="top-right"
          toastOptions={{
            style: {
              background: '#0a1a0a',
              color: '#00ff88',
              border: '1px solid #00ff8844',
            },
          }}
        />

        {/* Glass-morphism Header */}
        <header className="sticky top-0 z-50 backdrop-blur-md bg-black/40 border-b border-white/10 shadow-lg shadow-black/30">
          <div className="container mx-auto px-4 py-3 max-w-7xl">
            <div className="flex justify-between items-center">
              <div className="flex items-center gap-3">
                <RotatingEVLogo3D />
                <div>
                  <h1 className="text-xl md:text-2xl font-bold bg-gradient-to-r from-green-400 via-emerald-300 to-blue-400 bg-clip-text text-transparent">
                    EV Hiring Platform
                  </h1>
                  <p className="text-green-400/60 text-xs hidden sm:block tracking-wide">
                    AI-Powered 3D Recruitment Experience
                  </p>
                </div>
              </div>

              <div className="flex gap-3">
                <div className="glass-card px-4 py-2 rounded-xl text-center">
                  <p className="text-xs text-green-400/70">⭐ Shortlisted</p>
                  <p className="text-xl font-bold text-white">{shortlistedCount}</p>
                </div>
                <div className="glass-card px-4 py-2 rounded-xl text-center">
                  <p className="text-xs text-green-400/70">⏳ Pending</p>
                  <p className="text-xl font-bold text-white">{pendingCount}</p>
                </div>
              </div>
            </div>
          </div>
        </header>

        <main className="container mx-auto px-4 py-8 max-w-7xl">

          {/* Upload Section */}
          <motion.div
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="glass-card rounded-2xl p-6 mb-8"
          >
            <UploadForm onUploadComplete={handleUploadComplete} setLoading={setLoading} />
          </motion.div>

          {/* Loading Animation */}
          <AnimatePresence>
            {loading && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="flex justify-center items-center py-14 gap-4"
              >
                <div className="relative w-14 h-14">
                  <div className="absolute inset-0 border-4 border-green-500/20 border-t-green-400 rounded-full animate-spin" />
                  <div className="absolute inset-3 border-4 border-blue-500/20 border-t-blue-400 rounded-full animate-spin" style={{ animationDirection: 'reverse', animationDuration: '0.7s' }} />
                </div>
                <span className="text-green-300 text-lg font-medium tracking-wide">
                  AI is analyzing resumes in 3D space…
                </span>
              </motion.div>
            )}
          </AnimatePresence>

          {/* 3D EV Scooter */}
          <AnimatePresence>
            {rankedCandidates.length > 0 && !loading && (
              <motion.div
                initial={{ scale: 0.92, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ duration: 0.6 }}
                className="mb-8"
              >
                <EVScooter3D moving={true} direction={1} />
              </motion.div>
            )}
          </AnimatePresence>

          {/* 3D Floating Cards */}
          <AnimatePresence>
            {rankedCandidates.length > 0 && !loading && (
              <motion.div
                initial={{ y: 40, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ delay: 0.25, duration: 0.6 }}
                className="mb-8"
              >
                <div className="glass-card rounded-2xl p-5">
                  <h2 className="text-lg font-bold text-white mb-1 flex items-center gap-2">
                    <span className="text-2xl">🎯</span>
                    Top Candidates in 3D Space
                    <span className="text-xs text-green-400/70 ml-1 font-normal">hover to preview</span>
                  </h2>
                  <p className="text-xs text-gray-500 mb-4">Showing top {Math.min(6, rankedCandidates.length)} candidates</p>

                  <FloatingCards3D
                    candidates={rankedCandidates.slice(0, 6)}
                    onCardHover={setHoveredCandidate}
                  />

                  {/* Hover Info Panel */}
                  <AnimatePresence>
                    {hoveredCandidate && (
                      <motion.div
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: 10 }}
                        transition={{ duration: 0.2 }}
                        className="mt-4 p-4 rounded-xl border border-green-500/20"
                        style={{ background: 'linear-gradient(135deg, rgba(0,200,83,0.08), rgba(0,145,234,0.08))' }}
                      >
                        <div className="flex justify-between items-start">
                          <div>
                            <p className="text-green-400/70 text-xs uppercase tracking-widest mb-1">Selected Candidate</p>
                            <p className="text-white font-bold text-lg leading-tight">{hoveredCandidate.name}</p>
                            <p className="text-gray-400 text-sm">{hoveredCandidate.email}</p>
                            {hoveredCandidate.experience_years > 0 && (
                              <p className="text-gray-500 text-xs mt-1">🗓 {hoveredCandidate.experience_years} years experience</p>
                            )}
                          </div>
                          <div className="text-right">
                            <p className="text-4xl font-bold text-green-400 tabular-nums">{hoveredCandidate.match_score}%</p>
                            <p className="text-gray-500 text-xs">Match Score</p>
                            <p className="text-gray-400 text-xs mt-1">Rank #{hoveredCandidate.rank}</p>
                          </div>
                        </div>
                        {hoveredCandidate.skills?.length > 0 && (
                          <div className="flex flex-wrap gap-1.5 mt-3">
                            {hoveredCandidate.skills.slice(0, 6).map(skill => (
                              <span
                                key={skill}
                                className="px-2 py-0.5 rounded-full text-xs"
                                style={{ background: 'rgba(0,200,83,0.12)', color: '#00ff88', border: '1px solid rgba(0,200,83,0.25)' }}
                              >
                                {skill}
                              </span>
                            ))}
                          </div>
                        )}
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* View Toggle Tabs */}
          {rankedCandidates.length > 0 && !loading && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.4 }}
              className="flex gap-1 mb-6 p-1 glass-card rounded-xl w-fit"
            >
              {[
                { key: 'ranking', label: `📊 Rankings (${rankedCandidates.length})` },
                { key: 'shortlist', label: `⭐ Shortlist (${shortlistedCount})` },
              ].map(tab => (
                <button
                  key={tab.key}
                  onClick={() => setCurrentView(tab.key)}
                  className={`px-5 py-2 rounded-lg text-sm font-semibold transition-all duration-200 ${
                    currentView === tab.key
                      ? 'bg-green-500 text-black shadow-lg shadow-green-500/30'
                      : 'text-gray-400 hover:text-white'
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </motion.div>
          )}

          {/* Ranking Table */}
          {currentView === 'ranking' && rankedCandidates.length > 0 && !loading && (
            <Suspense fallback={<div className="text-green-400 text-center py-8">Loading rankings…</div>}>
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.1 }}>
                <RankingTable
                  candidates={rankedCandidates}
                  jobSkills={jobSkills}
                  onShortlist={handleShortlistToggle}
                />
              </motion.div>
            </Suspense>
          )}

          {/* Shortlist Panel */}
          {currentView === 'shortlist' && rankedCandidates.length > 0 && !loading && (
            <Suspense fallback={<div className="text-green-400 text-center py-8">Loading shortlist…</div>}>
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.1 }}>
                <ShortlistPanel
                  candidates={rankedCandidates.filter(c => c.status === 'shortlisted')}
                />
              </motion.div>
            </Suspense>
          )}

          {/* Empty State */}
          {!loading && rankedCandidates.length === 0 && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.3 }}
              className="text-center py-20"
            >
              <div className="text-7xl mb-5 animate-bounce">⚡</div>
              <h2 className="text-3xl font-bold bg-gradient-to-r from-green-400 to-blue-400 bg-clip-text text-transparent mb-3">
                EV Hiring Platform
              </h2>
              <p className="text-gray-400 text-lg max-w-md mx-auto">
                Upload resumes and a job description to get AI-powered candidate rankings in 3D
              </p>
            </motion.div>
          )}
        </main>
      </div>
    </div>
  );
}

export default App;
