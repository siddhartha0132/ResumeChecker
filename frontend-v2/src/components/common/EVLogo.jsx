import React from 'react';
import { motion } from 'framer-motion';

export default function EVLogo({ size = 80, animate = true }) {
  const Wrapper = animate ? motion.div : 'div';
  return (
    <Wrapper
      animate={animate ? { rotate: 360 } : undefined}
      transition={animate ? { duration: 20, repeat: Infinity, ease: 'linear' } : undefined}
      style={{ width: size, height: size }}
      className="relative flex items-center justify-center"
    >
      <svg viewBox="0 0 100 100" width={size} height={size}>
        {/* Outer ring */}
        <circle cx="50" cy="50" r="46" fill="none" stroke="#00C853" strokeWidth="3" strokeDasharray="8 4" />
        {/* Inner ring */}
        <circle cx="50" cy="50" r="36" fill="none" stroke="#00ff88" strokeWidth="1.5" opacity="0.5" />
        {/* EV text */}
        <text x="50" y="44" textAnchor="middle" fill="#00C853"
          fontFamily="Space Grotesk, sans-serif" fontWeight="700" fontSize="22">EV</text>
        {/* Lightning bolt */}
        <polygon points="54,52 48,52 51,62 45,62 50,72 56,62 52,62"
          fill="#FFD600" opacity="0.9" />
        {/* Orbit dots */}
        {[0,60,120,180,240,300].map((deg, i) => {
          const rad = (deg * Math.PI) / 180;
          return (
            <circle key={i}
              cx={50 + 46 * Math.cos(rad)}
              cy={50 + 46 * Math.sin(rad)}
              r="2.5" fill="#00C853" opacity="0.7" />
          );
        })}
      </svg>
    </Wrapper>
  );
}
