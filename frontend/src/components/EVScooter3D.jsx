import React, { useRef, useEffect, useState } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Float, Html } from '@react-three/drei';

function EVScooterModel({ moving, direction }) {
  const groupRef = useRef();
  const frontWheelRef = useRef();
  const rearWheelRef = useRef();
  const wheelAngle = useRef(0);

  useFrame(() => {
    if (!moving) return;

    wheelAngle.current += direction * 0.08;

    if (frontWheelRef.current) frontWheelRef.current.rotation.x = wheelAngle.current;
    if (rearWheelRef.current)  rearWheelRef.current.rotation.x  = wheelAngle.current;

    if (groupRef.current) {
      let newX = groupRef.current.position.x + direction * 0.012;
      if (newX > 4.5)  newX = -4.5;
      if (newX < -4.5) newX = 4.5;
      groupRef.current.position.x = newX;
    }
  });

  return (
    <group ref={groupRef} position={[0, -0.8, 0]}>
      {/* Body */}
      <mesh position={[0, 0.1, 0]} castShadow>
        <boxGeometry args={[1.2, 0.22, 0.75]} />
        <meshStandardMaterial color="#00C853" metalness={0.7} roughness={0.25} />
      </mesh>

      {/* Deck */}
      <mesh position={[-0.15, -0.18, 0]} castShadow>
        <boxGeometry args={[1.55, 0.09, 0.58]} />
        <meshStandardMaterial color="#1B5E20" metalness={0.5} roughness={0.4} />
      </mesh>

      {/* Handlebar stem */}
      <mesh position={[0.62, 0.55, 0]} castShadow>
        <cylinderGeometry args={[0.045, 0.045, 1.0, 8]} />
        <meshStandardMaterial color="#2a2a2a" metalness={0.85} roughness={0.15} />
      </mesh>

      {/* Handlebars */}
      <mesh position={[0.62, 1.05, 0]} castShadow>
        <boxGeometry args={[0.12, 0.07, 0.55]} />
        <meshStandardMaterial color="#2a2a2a" metalness={0.85} roughness={0.15} />
      </mesh>

      {/* Front wheel */}
      <group ref={frontWheelRef} position={[0.95, -0.38, 0]}>
        <mesh rotation={[0, 0, Math.PI / 2]} castShadow>
          <cylinderGeometry args={[0.34, 0.34, 0.1, 32]} />
          <meshStandardMaterial color="#1a1a1a" metalness={0.9} roughness={0.1} />
        </mesh>
        <mesh rotation={[0, 0, Math.PI / 2]}>
          <cylinderGeometry args={[0.14, 0.14, 0.12, 16]} />
          <meshStandardMaterial color="#FFD600" metalness={0.6} roughness={0.2} />
        </mesh>
      </group>

      {/* Rear wheel */}
      <group ref={rearWheelRef} position={[-0.62, -0.38, 0]}>
        <mesh rotation={[0, 0, Math.PI / 2]} castShadow>
          <cylinderGeometry args={[0.34, 0.34, 0.1, 32]} />
          <meshStandardMaterial color="#1a1a1a" metalness={0.9} roughness={0.1} />
        </mesh>
        <mesh rotation={[0, 0, Math.PI / 2]}>
          <cylinderGeometry args={[0.14, 0.14, 0.12, 16]} />
          <meshStandardMaterial color="#FFD600" metalness={0.6} roughness={0.2} />
        </mesh>
      </group>

      {/* Battery pack (glowing) */}
      <mesh position={[0, -0.12, 0.32]} castShadow>
        <boxGeometry args={[0.58, 0.14, 0.38]} />
        <meshStandardMaterial
          color="#00ff88"
          emissive="#00ff44"
          emissiveIntensity={0.35}
          metalness={0.5}
        />
      </mesh>

      {/* Speed lines */}
      {moving && direction > 0 && [...Array(5)].map((_, i) => (
        <mesh key={i} position={[-1.3 - i * 0.28, -0.05 + (i % 2) * 0.1, 0]}>
          <boxGeometry args={[0.18, 0.018, 0.06]} />
          <meshStandardMaterial color="#00ff88" emissive="#00ff44" emissiveIntensity={0.6} transparent opacity={0.7 - i * 0.12} />
        </mesh>
      ))}
    </group>
  );
}

function ChargingHUD() {
  const [chargeLevel, setChargeLevel] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setChargeLevel(prev => (prev >= 100 ? 0 : prev + 1));
    }, 45);
    return () => clearInterval(interval);
  }, []);

  return (
    <Float speed={1.5} rotationIntensity={0.3} floatIntensity={0.5}>
      <Html position={[0, 1.6, 0]} center>
        <div className="bg-black/70 backdrop-blur-sm rounded-xl px-4 py-2 text-center border border-green-500/30 shadow-lg shadow-green-500/10">
          <div className="text-green-400 text-xs font-mono tracking-widest mb-1">⚡ CHARGING</div>
          <div className="w-28 h-2 bg-gray-800 rounded-full overflow-hidden">
            <div
              className="h-full rounded-full transition-all duration-75"
              style={{
                width: `${chargeLevel}%`,
                background: `linear-gradient(90deg, #00C853, ${chargeLevel > 80 ? '#FFD600' : '#00ff88'})`,
              }}
            />
          </div>
          <div className="text-green-300 text-xs font-mono mt-1">{chargeLevel}%</div>
        </div>
      </Html>
    </Float>
  );
}

export default function EVScooter3D({ moving = true, direction = 1 }) {
  return (
    <div className="h-56 w-full rounded-2xl overflow-hidden shadow-2xl border border-green-500/20">
      <Canvas
        camera={{ position: [0, 1.2, 5.5], fov: 48 }}
        style={{ background: 'linear-gradient(135deg, #050f05 0%, #0a1f0a 100%)' }}
        shadows
      >
        <ambientLight intensity={0.5} />
        <pointLight position={[8, 8, 8]} intensity={1.2} />
        <pointLight position={[-5, 2, 3]} color="#00ff88" intensity={0.6} />
        <directionalLight position={[0, 6, 5]} intensity={0.9} castShadow />
        <EVScooterModel moving={moving} direction={direction} />
        <ChargingHUD />
        {/* Ground */}
        <mesh position={[0, -1.25, 0]} rotation={[-Math.PI / 2, 0, 0]} receiveShadow>
          <planeGeometry args={[20, 10]} />
          <meshStandardMaterial color="#050f05" transparent opacity={0.6} />
        </mesh>
      </Canvas>
    </div>
  );
}
