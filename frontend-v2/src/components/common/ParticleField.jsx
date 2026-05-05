import React, { useRef, useMemo } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Points, PointMaterial } from '@react-three/drei';
import * as THREE from 'three';

function Particles({ count = 1500, dark = true }) {
  const ref = useRef();
  const positions = useMemo(() => {
    const pos = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      pos[i * 3]     = (Math.random() - 0.5) * 180;
      pos[i * 3 + 1] = (Math.random() - 0.5) * 90;
      pos[i * 3 + 2] = (Math.random() - 0.5) * 90 - 40;
    }
    return pos;
  }, [count]);

  useFrame(({ clock }) => {
    if (ref.current) {
      ref.current.rotation.y = clock.getElapsedTime() * 0.018;
      ref.current.rotation.x = Math.sin(clock.getElapsedTime() * 0.009) * 0.08;
    }
  });

  return (
    <Points ref={ref} positions={positions}>
      <PointMaterial
        transparent size={0.28} sizeAttenuation depthWrite={false}
        opacity={dark ? 0.55 : 0.35}
        color={dark ? '#00ff88' : '#00C853'}
        blending={THREE.AdditiveBlending}
      />
    </Points>
  );
}

export default function ParticleField({ dark = true, className = '' }) {
  return (
    <div className={`fixed inset-0 -z-10 ${className}`}>
      <Canvas
        camera={{ position: [0, 0, 28], fov: 60 }}
        style={{
          background: dark
            ? 'linear-gradient(135deg, #050f05 0%, #0a1a0a 60%, #050a14 100%)'
            : 'linear-gradient(135deg, #f0faf0 0%, #e8f5e9 100%)',
        }}
      >
        <ambientLight intensity={0.4} />
        <Particles dark={dark} />
      </Canvas>
    </div>
  );
}
