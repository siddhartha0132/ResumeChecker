import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import EVLogo from '../common/EVLogo';
import ParticleField from '../common/ParticleField';

const MESSAGE = "⚡ Welcome to EVisionAstraa – India's fastest-growing EV technology company. We're building the future of electric mobility, one innovation at a time. Join us in revolutionizing sustainable transportation and shaping a cleaner, smarter world.";

const STATS = [
  { value: '500+', label: 'Engineers' },
  { value: '12',   label: 'EV Models' },
  { value: '98%',  label: 'Satisfaction' },
  { value: '2030', label: 'Net Zero Goal' },
];

export default function CompanyDebrief({ onComplete }) {
  const [typed, setTyped]         = useState('');
  const [showCTA, setShowCTA]     = useState(false);
  const [showStats, setShowStats] = useState(false);

  useEffect(() => {
    let i = 0;
    const t = setInterval(() => {
      if (i < MESSAGE.length) {
        setTyped(MESSAGE.slice(0, ++i));
      } else {
        clearInterval(t);
        setTimeout(() => setShowStats(true), 300);
        setTimeout(() => setShowCTA(true), 700);
      }
    }, 28);
    return () => clearInterval(t);
  }, []);

  return (
    <div className="min-h-screen flex items-center justify-center relative overflow-hidden">
      <ParticleField dark />

      <div className="relative z-10 max-w-3xl mx-auto px-6 text-center">
        {/* Logo */}
        <motion.div
          initial={{ scale: 0, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ type: 'spring', stiffness: 120 }}
          className="flex justify-center mb-8"
        >
          <EVLogo size={110} animate />
        </motion.div>

        {/* Company name */}
        <motion.h1
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-4xl md:text-5xl font-heading font-bold mb-6"
          style={{ background: 'linear-gradient(135deg, #00C853, #00ff88, #2979FF)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}
        >
          EVisionAstraa
        </motion.h1>

        {/* Typing text */}
        <div className="text-white/80 text-lg md:text-xl leading-relaxed font-light mb-8 min-h-[80px]">
          {typed}
          <span className="animate-pulse text-green-400">|</span>
        </div>

        {/* Stats */}
        {showStats && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="grid grid-cols-4 gap-4 mb-10"
          >
            {STATS.map((s, i) => (
              <motion.div
                key={s.label}
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: i * 0.1 }}
                className="glass-card rounded-xl py-3 px-2"
              >
                <p className="text-2xl font-bold text-green-400 font-mono">{s.value}</p>
                <p className="text-xs text-gray-400 mt-0.5">{s.label}</p>
              </motion.div>
            ))}
          </motion.div>
        )}

        {/* CTA */}
        {showCTA && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="flex flex-col sm:flex-row gap-4 justify-center"
          >
            <button
              onClick={onComplete}
              className="btn-primary text-lg px-10 py-3 rounded-full shadow-2xl shadow-green-500/30"
            >
              Explore Opportunities →
            </button>
          </motion.div>
        )}
      </div>
    </div>
  );
}
