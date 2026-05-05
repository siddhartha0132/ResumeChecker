import React, { useRef, useState } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Html, Float } from '@react-three/drei';

function CandidateCard3D({ candidate, index, onHover }) {
  const cardRef = useRef();
  const [hovered, setHovered] = useState(false);

  // Grid layout: 3 columns
  const col = index % 3;
  const row = Math.floor(index / 3);
  const posX = (col - 1) * 2.4;
  const posZ = row * -2.8;

  const matchColor =
    candidate.match_score >= 80 ? '#00ff88' :
    candidate.match_score >= 60 ? '#ffcc00' : '#ff6644';

  useFrame(({ clock }) => {
    if (cardRef.current && !hovered) {
      cardRef.current.rotation.y = Math.sin(clock.getElapsedTime() * 0.5 + index * 1.2) * 0.08;
      cardRef.current.position.y = Math.sin(clock.getElapsedTime() * 0.7 + index) * 0.12;
    }
  });

  return (
    <group
      ref={cardRef}
      position={[posX, 0, posZ]}
      onPointerEnter={() => { setHovered(true); onHover(candidate); }}
      onPointerLeave={() => setHovered(false)}
    >
      {/* Card body */}
      <mesh castShadow>
        <boxGeometry args={[1.7, 2.1, 0.08]} />
        <meshStandardMaterial
          color={hovered ? '#0d2a1a' : '#071a0e'}
          metalness={0.6}
          roughness={0.3}
          emissive={hovered ? matchColor : '#000000'}
          emissiveIntensity={hovered ? 0.15 : 0}
        />
      </mesh>

      {/* Glowing border frame */}
      <mesh position={[0, 0, 0.05]}>
        <boxGeometry args={[1.74, 2.14, 0.02]} />
        <meshStandardMaterial
          color={matchColor}
          emissive={matchColor}
          emissiveIntensity={hovered ? 0.6 : 0.18}
          transparent
          opacity={0.85}
        />
      </mesh>

      {/* Score ring */}
      <mesh position={[0, 0.65, 0.06]} rotation={[0, 0, 0]}>
        <torusGeometry args={[0.38, 0.025, 24, 64]} />
        <meshStandardMaterial
          color={matchColor}
          emissive={matchColor}
          emissiveIntensity={hovered ? 0.8 : 0.4}
        />
      </mesh>

      {/* Score + name HTML overlay */}
      <Html position={[0, 0.65, 0.12]} center>
        <div className="text-center pointer-events-none select-none">
          <div
            className="text-lg font-bold tabular-nums"
            style={{ color: matchColor, textShadow: `0 0 8px ${matchColor}` }}
          >
            {candidate.match_score}%
          </div>
        </div>
      </Html>

      <Html position={[0, -0.1, 0.12]} center>
        <div className="text-center pointer-events-none select-none w-36">
          <div className="text-white font-semibold text-xs truncate leading-tight">
            {candidate.name || 'Unknown'}
          </div>
          <div className="text-gray-400 text-xs mt-0.5">
            #{candidate.rank} · {candidate.experience_years || 0}yr exp
          </div>
        </div>
      </Html>

      {/* Skill dots */}
      <Html position={[0, -0.72, 0.12]} center>
        <div className="flex flex-wrap justify-center gap-1 w-36 pointer-events-none select-none">
          {(candidate.skills || []).slice(0, 3).map(skill => (
            <span
              key={skill}
              className="text-xs px-1.5 py-0.5 rounded-full"
              style={{
                background: `${matchColor}22`,
                color: matchColor,
                border: `1px solid ${matchColor}44`,
                fontSize: '9px',
              }}
            >
              {skill}
            </span>
          ))}
        </div>
      </Html>
    </group>
  );
}

export default function FloatingCards3D({ candidates, onCardHover }) {
  return (
    <div className="h-80 w-full rounded-2xl overflow-hidden border border-green-500/10">
      <Canvas
        camera={{ position: [0, 0.5, 9], fov: 48 }}
        style={{ background: 'transparent' }}
      >
        <ambientLight intensity={0.6} />
        <pointLight position={[10, 10, 10]} intensity={1} />
        <pointLight position={[-5, 2, 3]} color="#00ff88" intensity={0.5} />
        {candidates.slice(0, 6).map((candidate, idx) => (
          <CandidateCard3D
            key={candidate.candidate_id ?? idx}
            candidate={candidate}
            index={idx}
            onHover={onCardHover}
          />
        ))}
      </Canvas>
    </div>
  );
}
