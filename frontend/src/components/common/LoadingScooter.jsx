import React from 'react';
import { motion } from 'framer-motion';

export default function LoadingScooter({ progress = 0, label = 'AI is analyzing your resume…' }) {
  return (
    <div className="w-full">
      {/* Track */}
      <div className="relative h-28 bg-gray-900 rounded-2xl overflow-hidden border border-green-500/20">
        {/* Road surface */}
        <div className="absolute bottom-0 w-full h-10 bg-gray-800" />
        {/* Road line */}
        <motion.div
          className="absolute bottom-9 h-0.5 w-full"
          style={{ background: 'repeating-linear-gradient(90deg, #FFD600 0, #FFD600 20px, transparent 20px, transparent 40px)' }}
          animate={{ x: [0, -40] }}
          transition={{ repeat: Infinity, duration: 0.6, ease: 'linear' }}
        />

        {/* Speed lines */}
        {progress > 5 && (
          <motion.div
            className="absolute top-1/2 -translate-y-1/2 flex gap-2"
            style={{ left: `${Math.max(0, progress - 18)}%` }}
            animate={{ opacity: [0.8, 0.2, 0.8] }}
            transition={{ repeat: Infinity, duration: 0.4 }}
          >
            {[16, 10, 6].map((w, i) => (
              <div key={i} className="h-0.5 bg-green-400 rounded-full" style={{ width: w }} />
            ))}
          </motion.div>
        )}

        {/* Scooter */}
        <motion.div
          className="absolute bottom-8"
          animate={{ x: `${progress}%` }}
          transition={{ type: 'spring', stiffness: 40, damping: 18 }}
          style={{ left: 0 }}
        >
          <svg width="64" height="44" viewBox="0 0 80 55">
            {/* Body */}
            <rect x="18" y="12" width="42" height="14" rx="5" fill="#00C853" />
            <rect x="14" y="22" width="52" height="9" rx="3" fill="#1B5E20" />
            {/* Stem */}
            <rect x="52" y="3" width="4" height="14" fill="#444" />
            {/* Handlebars */}
            <rect x="46" y="1" width="16" height="5" rx="2" fill="#444" />
            {/* Front wheel */}
            <motion.g
              animate={{ rotate: progress * 8 }}
              style={{ transformOrigin: '62px 38px' }}
            >
              <circle cx="62" cy="38" r="9" fill="#222" />
              <circle cx="62" cy="38" r="3.5" fill="#FFD600" />
              <line x1="62" y1="29" x2="62" y2="47" stroke="#555" strokeWidth="1.5" />
              <line x1="53" y1="38" x2="71" y2="38" stroke="#555" strokeWidth="1.5" />
            </motion.g>
            {/* Rear wheel */}
            <motion.g
              animate={{ rotate: progress * 8 }}
              style={{ transformOrigin: '20px 38px' }}
            >
              <circle cx="20" cy="38" r="9" fill="#222" />
              <circle cx="20" cy="38" r="3.5" fill="#FFD600" />
              <line x1="20" y1="29" x2="20" y2="47" stroke="#555" strokeWidth="1.5" />
              <line x1="11" y1="38" x2="29" y2="38" stroke="#555" strokeWidth="1.5" />
            </motion.g>
            {/* Battery glow */}
            <rect x="28" y="24" width="18" height="6" rx="2" fill="#00ff88" opacity="0.6" />
            {/* Headlight */}
            <circle cx="66" cy="18" r="3" fill="#FFD600">
              <animate attributeName="opacity" values="1;0.4;1" dur="0.8s" repeatCount="indefinite" />
            </circle>
          </svg>
        </motion.div>
      </div>

      {/* Progress bar */}
      <div className="mt-3">
        <div className="flex justify-between text-xs text-gray-500 mb-1">
          <span>{label}</span>
          <span className="font-mono font-semibold text-green-600">{progress}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
          <motion.div
            className="h-full rounded-full"
            style={{ background: 'linear-gradient(90deg, #00C853, #00ff88)' }}
            animate={{ width: `${progress}%` }}
            transition={{ duration: 0.3 }}
          />
        </div>
      </div>
    </div>
  );
}
