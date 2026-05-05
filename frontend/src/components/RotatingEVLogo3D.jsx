import React, { useRef, useState } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Text3D, OrbitControls, Center } from '@react-three/drei';
import * as THREE from 'three';

function EVLogo3D({ rotationSpeed = 0.012 }) {
  const groupRef = useRef();
  const [hovered, setHovered] = useState(false);

  useFrame((state) => {
    if (groupRef.current) {
      if (!hovered) {
        groupRef.current.rotation.y += rotationSpeed;
      }
      groupRef.current.rotation.x = Math.sin(state.clock.getElapsedTime() * 0.8) * 0.12;
    }
  });

  const orbitParticles = [...Array(10)].map((_, i) => {
    const angle = (i / 10) * Math.PI * 2;
    return { x: Math.cos(angle) * 1.55, y: Math.sin(angle) * 1.55 };
  });

  return (
    <group
      ref={groupRef}
      onPointerEnter={() => setHovered(true)}
      onPointerLeave={() => setHovered(false)}
    >
      {/* Outer glowing ring */}
      <mesh rotation={[Math.PI / 2, 0, 0]}>
        <torusGeometry args={[1.2, 0.05, 32, 128]} />
        <meshStandardMaterial
          color="#00ff88"
          emissive="#00ff44"
          emissiveIntensity={hovered ? 1.2 : 0.4}
          metalness={0.8}
          roughness={0.2}
        />
      </mesh>

      {/* Inner ring */}
      <mesh rotation={[Math.PI / 2, 0, 0]}>
        <torusGeometry args={[0.85, 0.025, 32, 128]} />
        <meshStandardMaterial
          color="#00cc66"
          emissive="#00ff44"
          emissiveIntensity={0.5}
          metalness={0.9}
        />
      </mesh>

      {/* EV Text */}
      <Center position={[0, -0.18, 0.08]}>
        <Text3D
          font="/fonts/helvetiker_regular.typeface.json"
          size={0.55}
          height={0.08}
          curveSegments={24}
          bevelEnabled
          bevelThickness={0.015}
          bevelSize={0.008}
          bevelSegments={6}
        >
          EV
          <meshStandardMaterial
            color={hovered ? '#ffffff' : '#00ff88'}
            emissive="#00ff44"
            emissiveIntensity={hovered ? 0.8 : 0.4}
            metalness={0.9}
            roughness={0.1}
          />
        </Text3D>
      </Center>

      {/* Lightning bolt */}
      <mesh position={[0.52, 0.22, 0.18]} scale={0.38} rotation={[0, 0, -0.3]}>
        <coneGeometry args={[0.28, 0.55, 4]} />
        <meshStandardMaterial
          color="#ffdd00"
          emissive="#ffaa00"
          emissiveIntensity={0.9}
        />
      </mesh>

      {/* Orbit particles */}
      {orbitParticles.map((p, i) => (
        <mesh key={i} position={[p.x, p.y, 0]} scale={0.045}>
          <sphereGeometry args={[1, 8, 8]} />
          <meshStandardMaterial
            color="#00ff88"
            emissive="#00ff44"
            emissiveIntensity={0.5}
          />
        </mesh>
      ))}
    </group>
  );
}

export default function RotatingEVLogo3D() {
  return (
    <div className="w-20 h-20 md:w-24 md:h-24 flex-shrink-0">
      <Canvas camera={{ position: [0, 0, 4.5], fov: 50 }}>
        <ambientLight intensity={0.6} />
        <pointLight position={[5, 5, 5]} intensity={1.2} />
        <pointLight position={[-5, -5, -5]} color="#00ff88" intensity={0.6} />
        <EVLogo3D />
        <OrbitControls enableZoom={false} enablePan={false} autoRotate={false} />
      </Canvas>
    </div>
  );
}
