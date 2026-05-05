/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'ev-primary': '#00C853',
        'ev-secondary': '#0091EA',
        'ev-dark': '#1B5E20',
      }
    },
  },
  plugins: [],
}
