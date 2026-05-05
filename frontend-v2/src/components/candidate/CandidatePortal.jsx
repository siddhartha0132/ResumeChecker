import React, { useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import CompanyDebrief from './CompanyDebrief';
import RoleSelector from './RoleSelector';
import ResumeUploader from './ResumeUploader';
import ScoreDisplay from './ScoreDisplay';
import ParticleField from '../common/ParticleField';

const STEPS = ['debrief', 'role_select', 'upload', 'results'];

function StepIndicator({ step }) {
  const labels = ['Welcome', 'Choose Role', 'Upload Resume', 'Results'];
  const idx = STEPS.indexOf(step);
  if (idx < 1) return null;
  return (
    <div className="flex items-center justify-center gap-2 py-4">
      {labels.slice(1).map((l, i) => (
        <React.Fragment key={l}>
          <div className={`flex items-center gap-1.5 text-xs font-medium ${i <= idx - 1 ? 'text-ev-primary' : 'text-gray-400'}`}>
            <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${
              i < idx - 1 ? 'bg-ev-primary text-white' :
              i === idx - 1 ? 'bg-ev-primary text-white ring-2 ring-green-300' :
              'bg-gray-200 text-gray-500'
            }`}>{i + 1}</div>
            <span className="hidden sm:inline">{l}</span>
          </div>
          {i < 2 && <div className={`h-px w-8 ${i < idx - 1 ? 'bg-ev-primary' : 'bg-gray-200'}`} />}
        </React.Fragment>
      ))}
    </div>
  );
}

export default function CandidatePortal() {
  const [step, setStep]           = useState('debrief');
  const [selectedRole, setRole]   = useState(null);
  const [scoreData, setScoreData] = useState(null);

  const handleRoleSelect = (role) => {
    setRole(role);
    setStep('upload');
  };

  const handleScoreReceived = (data) => {
    setScoreData(data);
    setStep('results');
  };

  const handleRestart = () => {
    setStep('role_select');
    setRole(null);
    setScoreData(null);
  };

  return (
    <div className="min-h-screen relative">
      {step !== 'debrief' && <ParticleField dark={false} />}

      <div className="relative z-10">
        {/* Step indicator */}
        {step !== 'debrief' && (
          <div className="bg-white/80 backdrop-blur-sm border-b border-gray-200 sticky top-0 z-20">
            <div className="container mx-auto px-4">
              <StepIndicator step={step} />
            </div>
          </div>
        )}

        <AnimatePresence mode="wait">
          {/* ── Debrief ── */}
          {step === 'debrief' && (
            <motion.div key="debrief" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
              <CompanyDebrief onComplete={() => setStep('role_select')} />
            </motion.div>
          )}

          {/* ── Role Select ── */}
          {step === 'role_select' && (
            <motion.div key="roles"
              initial={{ opacity: 0, x: 40 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -40 }}
              className="container mx-auto px-4 py-8"
            >
              <RoleSelector selectedRole={selectedRole} onSelectRole={handleRoleSelect} />
            </motion.div>
          )}

          {/* ── Upload ── */}
          {step === 'upload' && selectedRole && (
            <motion.div key="upload"
              initial={{ opacity: 0, x: 40 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -40 }}
              className="container mx-auto px-4 py-10"
            >
              <div className="max-w-2xl mx-auto">
                <div className="text-center mb-8">
                  <span className="text-5xl">{selectedRole.emoji}</span>
                  <h2 className="text-3xl font-heading font-bold text-gray-800 mt-3">
                    Apply for {selectedRole.title}
                  </h2>
                  <p className="text-gray-500 mt-2">Upload your resume to get AI-powered analysis</p>
                </div>

                {/* JD preview */}
                <div className="bg-gray-50 border border-gray-200 rounded-2xl p-4 mb-6">
                  <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Job Description</p>
                  <p className="text-sm text-gray-600 leading-relaxed">{selectedRole.jd.substring(0, 220)}…</p>
                </div>

                <ResumeUploader
                  selectedRole={selectedRole}
                  jobDescription={selectedRole.jd}
                  onScoreReceived={handleScoreReceived}
                />

                <button
                  onClick={() => setStep('role_select')}
                  className="mt-4 text-sm text-gray-400 hover:text-gray-600 w-full text-center"
                >
                  ← Change role
                </button>
              </div>
            </motion.div>
          )}

          {/* ── Results ── */}
          {step === 'results' && scoreData && (
            <motion.div key="results"
              initial={{ opacity: 0, scale: 0.97 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0 }}
              className="container mx-auto px-4 py-10"
            >
              <ScoreDisplay data={scoreData} selectedRole={selectedRole} onRestart={handleRestart} />
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
