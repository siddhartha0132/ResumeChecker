import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Toaster } from 'react-hot-toast';
import CandidatePortal from './components/candidate/CandidatePortal';
import ManagerDashboard from './components/manager/ManagerDashboard';
import EVLogo from './components/common/EVLogo';
import ParticleField from './components/common/ParticleField';

function LandingPage({ onSelect }) {
  return (
    <div className="min-h-screen flex items-center justify-center relative overflow-hidden">
      <ParticleField dark />
      <div className="relative z-10 text-center px-6 max-w-2xl mx-auto">
        {/* Logo */}
        <motion.div
          initial={{ scale: 0, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ type: 'spring', stiffness: 100 }}
          className="flex justify-center mb-6"
        >
          <EVLogo size={120} animate />
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="text-5xl md:text-6xl font-heading font-bold mb-3"
          style={{ background: 'linear-gradient(135deg, #00C853, #00ff88, #2979FF)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}
        >
          EVisionAstraa
        </motion.h1>

        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="text-white/60 text-lg mb-12"
        >
          AI-Powered EV Hiring Platform
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7 }}
          className="grid grid-cols-1 sm:grid-cols-2 gap-6"
        >
          {/* Candidate Portal */}
          <motion.button
            whileHover={{ scale: 1.04, y: -4 }}
            whileTap={{ scale: 0.97 }}
            onClick={() => onSelect('candidate')}
            className="glass-card rounded-3xl p-8 text-left group cursor-pointer border border-green-500/20 hover:border-green-500/50 transition-all duration-300"
          >
            <div className="text-5xl mb-4">👤</div>
            <h2 className="text-2xl font-heading font-bold text-white mb-2 group-hover:text-green-400 transition-colors">
              Candidate Portal
            </h2>
            <p className="text-white/50 text-sm leading-relaxed">
              Apply for EV roles, upload your resume, and get instant AI-powered feedback on your match score.
            </p>
            <div className="mt-5 flex items-center gap-2 text-green-400 text-sm font-semibold">
              Apply Now <span className="group-hover:translate-x-1 transition-transform">→</span>
            </div>
          </motion.button>

          {/* Manager Dashboard */}
          <motion.button
            whileHover={{ scale: 1.04, y: -4 }}
            whileTap={{ scale: 0.97 }}
            onClick={() => onSelect('manager')}
            className="glass-card rounded-3xl p-8 text-left group cursor-pointer border border-blue-500/20 hover:border-blue-500/50 transition-all duration-300"
          >
            <div className="text-5xl mb-4">🏢</div>
            <h2 className="text-2xl font-heading font-bold text-white mb-2 group-hover:text-blue-400 transition-colors">
              HR Dashboard
            </h2>
            <p className="text-white/50 text-sm leading-relaxed">
              Review applicants, compare candidates side-by-side, shortlist top talent, and export reports.
            </p>
            <div className="mt-5 flex items-center gap-2 text-blue-400 text-sm font-semibold">
              Open Dashboard <span className="group-hover:translate-x-1 transition-transform">→</span>
            </div>
          </motion.button>
        </motion.div>

        {/* Feature pills */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1 }}
          className="flex flex-wrap justify-center gap-2 mt-10"
        >
          {['spaCy NER', 'TF-IDF Ranking', '50+ EV Skills', '3D Animations', 'PDF Export', 'OCR Support'].map(f => (
            <span key={f} className="text-xs px-3 py-1 rounded-full text-white/50 border border-white/10">
              {f}
            </span>
          ))}
        </motion.div>
      </div>
    </div>
  );
}

export default function App() {
  const [portal, setPortal] = useState(null); // null | 'candidate' | 'manager'

  return (
    <>
      <Toaster
        position="top-right"
        toastOptions={{
          style: { background: '#0a1a0a', color: '#00ff88', border: '1px solid #00ff8844' },
        }}
      />

      <AnimatePresence mode="wait">
        {portal === null && (
          <motion.div key="landing" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
            <LandingPage onSelect={setPortal} />
          </motion.div>
        )}

        {portal === 'candidate' && (
          <motion.div key="candidate" initial={{ opacity: 0, x: 40 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -40 }}>
            {/* Back button */}
            <button
              onClick={() => setPortal(null)}
              className="fixed top-4 left-4 z-50 bg-white/10 backdrop-blur-sm text-white px-3 py-1.5 rounded-xl text-sm hover:bg-white/20 transition border border-white/20"
            >
              ← Home
            </button>
            <CandidatePortal />
          </motion.div>
        )}

        {portal === 'manager' && (
          <motion.div key="manager" initial={{ opacity: 0, x: 40 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -40 }}>
            {/* Back button */}
            <button
              onClick={() => setPortal(null)}
              className="fixed top-4 left-4 z-50 bg-white/10 backdrop-blur-sm text-white px-3 py-1.5 rounded-xl text-sm hover:bg-white/20 transition border border-white/20"
            >
              ← Home
            </button>
            <ManagerDashboard />
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
