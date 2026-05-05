import React from 'react';

export default function Header({ shortlistedCount, pendingCount }) {
  return (
    <header className="bg-gradient-to-r from-ev-dark to-ev-primary shadow-lg">
      <div className="container mx-auto px-4 py-6 max-w-7xl">
        <div className="flex justify-between items-center">
          <div className="flex items-center gap-3">
            <div className="text-4xl">⚡</div>
            <div>
              <h1 className="text-2xl font-bold text-white">EV Hiring Platform</h1>
              <p className="text-green-100 text-sm">
                AI-Powered Resume Screening for Electric Vehicle Industry
              </p>
            </div>
          </div>

          <div className="flex gap-4">
            <div className="bg-white/20 rounded-lg px-4 py-2 text-center">
              <p className="text-xs text-green-100">Shortlisted</p>
              <p className="text-xl font-bold text-white">{shortlistedCount}</p>
            </div>
            <div className="bg-white/20 rounded-lg px-4 py-2 text-center">
              <p className="text-xs text-green-100">Pending Review</p>
              <p className="text-xl font-bold text-white">{pendingCount}</p>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
