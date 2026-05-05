import React from 'react';
import { EV_ROLES } from '../candidate/RoleSelector';

const ALL_ROLES = [{ id: 'all', emoji: '🌐', title: 'All Roles' }, ...EV_ROLES];

export default function RoleFilter({ selectedRole, onRoleChange, counts = {} }) {
  return (
    <div className="flex flex-wrap gap-2 mb-6">
      {ALL_ROLES.map(role => {
        const active = selectedRole === role.id;
        const count  = role.id === 'all' ? Object.values(counts).reduce((a, b) => a + b, 0) : (counts[role.id] || 0);
        return (
          <button
            key={role.id}
            onClick={() => onRoleChange(role.id)}
            className={`flex items-center gap-1.5 px-4 py-2 rounded-xl text-sm font-medium transition-all duration-200 ${
              active
                ? 'bg-ev-primary text-white shadow-lg shadow-green-500/25'
                : 'bg-white border border-gray-200 text-gray-600 hover:border-ev-primary hover:text-ev-primary'
            }`}
          >
            <span>{role.emoji}</span>
            <span>{role.title}</span>
            {count > 0 && (
              <span className={`text-xs px-1.5 py-0.5 rounded-full font-bold ${
                active ? 'bg-white/25 text-white' : 'bg-gray-100 text-gray-500'
              }`}>{count}</span>
            )}
          </button>
        );
      })}
    </div>
  );
}
