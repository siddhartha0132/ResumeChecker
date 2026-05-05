/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'ev-primary':      '#00C853',
        'ev-primary-dark': '#009624',
        'ev-secondary':    '#2979FF',
        'ev-accent':       '#FFD600',
        'ev-bg-dark':      '#0A0F0A',
        'ev-bg-light':     '#F5F9F5',
        'ev-card':         '#FFFFFF',
        'ev-text':         '#1A2E1A',
        'ev-text-light':   '#6B7B6B',
      },
      fontFamily: {
        heading: ["'Space Grotesk'", 'sans-serif'],
        body:    ["'Inter'",         'sans-serif'],
        mono:    ["'JetBrains Mono'", 'monospace'],
      },
      animation: {
        'spin-slow': 'spin 20s linear infinite',
        'pulse-slow': 'pulse 3s ease-in-out infinite',
      },
    },
  },
  plugins: [],
}
