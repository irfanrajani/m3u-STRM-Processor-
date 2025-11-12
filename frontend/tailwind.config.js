/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#f0fdfa',
          100: '#ccfbf1',
          200: '#99f6e4',
          300: '#5eead4',
          400: '#2dd4bf',
          500: '#14b8a6', // primary teal
          600: '#0d9488',
          700: '#0f766e',
          800: '#115e59',
          900: '#134e4a'
        },
        accent: {
          400: '#22d3ee',
          500: '#06b6d4',
          600: '#0891b2'
        },
        ocean: {
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8'
        },
        success: '#10b981',
        danger: '#f43f5e'
      },
      boxShadow: {
        'glow-brand': '0 0 0 2px rgba(20,184,166,0.3), 0 4px 12px rgba(0,0,0,0.15)'
      }
    },
  },
  plugins: [],
}
