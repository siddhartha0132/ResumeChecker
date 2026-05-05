import React, { useState } from 'react';
import { motion } from 'framer-motion';

export const EV_ROLES = [
  {
    id: 'battery_engineer',
    emoji: '🔋',
    title: 'Battery Engineer',
    description: 'Design and optimize lithium-ion battery packs, BMS, and thermal management systems.',
    requirements: ['Battery Management', 'BMS', 'Thermal Management', 'MATLAB'],
    jd: "We're seeking a Battery Engineer to design next-gen lithium-ion battery packs. Responsibilities include BMS development, thermal management, cell selection, and safety testing. Required: 3+ years battery experience, MATLAB proficiency, knowledge of battery chemistry and ISO 26262.",
  },
  {
    id: 'powertrain_engineer',
    emoji: '⚙️',
    title: 'Powertrain Engineer',
    description: 'Develop electric motors, inverters, and drivetrain systems for EVs.',
    requirements: ['Electric Motor', 'Inverter', 'Control Systems', 'Simulink'],
    jd: "Seeking a Powertrain Engineer to develop electric motors, inverters, and drivetrain systems. Must have experience with motor control algorithms, power electronics, and Simulink model-based design. 3+ years in EV powertrain required.",
  },
  {
    id: 'charging_infrastructure',
    emoji: '🔌',
    title: 'Charging Infrastructure Expert',
    description: 'Build and manage EV charging networks, CCS, and V2G systems.',
    requirements: ['EV Charging', 'CCS', 'OCPP', 'V2G'],
    jd: "Looking for a Charging Infrastructure Expert to design and deploy EV charging solutions. Experience with CCS, CHAdeMO, OCPP protocol, and V2G bidirectional charging required. Knowledge of ISO 15118 is a plus.",
  },
  {
    id: 'autonomy_adas',
    emoji: '🤖',
    title: 'ADAS / Autonomy Engineer',
    description: 'Develop autonomous driving features, sensor fusion, and perception systems.',
    requirements: ['ADAS', 'Sensor Fusion', 'LIDAR', 'Radar'],
    jd: "Hiring an ADAS Engineer to develop autonomous driving features. Must have experience with sensor fusion, LIDAR, radar, camera systems, and path planning algorithms. C++ and Python proficiency required.",
  },
  {
    id: 'embedded_software',
    emoji: '💻',
    title: 'Embedded Software Engineer',
    description: 'Build firmware for ECUs, CAN communication, and real-time systems.',
    requirements: ['Embedded C', 'AUTOSAR', 'CAN Bus', 'ISO 26262'],
    jd: "Seeking an Embedded Software Engineer for ECU firmware development. Must have strong Embedded C skills, AUTOSAR architecture knowledge, CAN Bus experience, and familiarity with ISO 26262 functional safety.",
  },
  {
    id: 'testing_validation',
    emoji: '🧪',
    title: 'Testing & Validation Engineer',
    description: 'HIL/SIL testing, vehicle validation, and ISO 26262 compliance.',
    requirements: ['HIL Testing', 'SIL Testing', 'dSPACE', 'ISO 26262'],
    jd: "Looking for a Testing & Validation Engineer for HIL/SIL testing of EV systems. Experience with dSPACE, NI LabVIEW, and ISO 26262 compliance testing required. Python scripting for test automation is a plus.",
  },
];

export default function RoleSelector({ onSelectRole, selectedRole }) {
  const [hovered, setHovered] = useState(null);

  return (
    <div className="py-8">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center mb-10"
      >
        <h2 className="text-4xl font-heading font-bold text-gray-800 mb-3">
          Choose Your <span className="text-ev-primary">Dream Role</span>
        </h2>
        <p className="text-gray-500 text-lg">Select the position you're applying for at EVisionAstraa</p>
      </motion.div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-6xl mx-auto">
        {EV_ROLES.map((role, i) => {
          const isSelected = selectedRole?.id === role.id;
          const isHovered  = hovered === role.id;
          return (
            <motion.div
              key={role.id}
              initial={{ opacity: 0, y: 24 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.08 }}
              onClick={() => onSelectRole(role)}
              onMouseEnter={() => setHovered(role.id)}
              onMouseLeave={() => setHovered(null)}
              className={`cursor-pointer rounded-2xl p-6 transition-all duration-300 card-hover ${
                isSelected
                  ? 'bg-ev-primary text-white shadow-2xl shadow-green-500/30 scale-105'
                  : 'bg-white border border-gray-200 hover:border-ev-primary'
              }`}
            >
              <div className="text-4xl mb-3">{role.emoji}</div>
              <h3 className={`text-xl font-heading font-bold mb-2 ${isSelected ? 'text-white' : 'text-gray-800'}`}>
                {role.title}
              </h3>
              <p className={`text-sm mb-4 leading-relaxed ${isSelected ? 'text-green-100' : 'text-gray-500'}`}>
                {role.description}
              </p>
              <div className="flex flex-wrap gap-1.5">
                {role.requirements.map(req => (
                  <span
                    key={req}
                    className={`text-xs px-2.5 py-1 rounded-full font-medium ${
                      isSelected ? 'bg-white/20 text-white' : 'bg-gray-100 text-gray-600'
                    }`}
                  >
                    {req}
                  </span>
                ))}
              </div>
              {isSelected && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="mt-4 text-sm font-semibold text-white/90 flex items-center gap-1"
                >
                  ✅ Selected — Click to continue ↓
                </motion.div>
              )}
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
