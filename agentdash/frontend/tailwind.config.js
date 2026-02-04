/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        dark: {
          900: '#0d0a1a',
          800: '#1a1625',
          700: '#252036',
          600: '#2f2a42',
        },
        accent: {
          green: '#22c55e',
          cyan: '#06b6d4',
          purple: '#a855f7',
          orange: '#f97316',
          pink: '#ec4899',
        }
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
      },
      keyframes: {
        glow: {
          '0%': { boxShadow: '0 0 5px #22c55e, 0 0 10px #22c55e' },
          '100%': { boxShadow: '0 0 20px #22c55e, 0 0 30px #22c55e' },
        }
      }
    },
  },
  plugins: [],
}
