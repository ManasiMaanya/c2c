/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        cyber: {
          bg: '#050811',
          card: '#0b0f19',
          cardHover: '#111726',
          border: '#1e293b',
          borderGlow: '#38bdf8',
          accent: '#06b6d4',
          accentGlow: 'rgba(6, 182, 212, 0.15)',
          red: '#ef4444',
          redGlow: 'rgba(239, 68, 68, 0.2)',
          amber: '#f59e0b',
          green: '#10b981',
          greenGlow: 'rgba(16, 185, 129, 0.2)',
          text: '#94a3b8',
          heading: '#f8fafc',
          muted: '#64748b'
        }
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'Fira Code', 'ui-monospace', 'monospace'],
        sans: ['Inter', 'Plus Jakarta Sans', 'system-ui', 'sans-serif']
      },
      boxShadow: {
        'glow-cyan': '0 0 20px -3px rgba(6, 182, 212, 0.3)',
        'glow-red': '0 0 25px -3px rgba(239, 68, 68, 0.4)',
        'glow-green': '0 0 20px -3px rgba(16, 185, 129, 0.3)',
        'cyber-card': '0 8px 32px 0 rgba(0, 0, 0, 0.37)'
      },
      backgroundImage: {
        'grid-pattern': "radial-gradient(rgba(56, 189, 248, 0.08) 1px, transparent 0)",
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
      },
      animation: {
        'pulse-glow': 'pulseGlow 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'radar-sweep': 'radarSweep 4s linear infinite',
      },
      keyframes: {
        pulseGlow: {
          '0%, 100%': { opacity: 1, filter: 'drop-shadow(0 0 8px rgba(239,68,68,0.8))' },
          '50%': { opacity: 0.4, filter: 'drop-shadow(0 0 2px rgba(239,68,68,0.3))' },
        },
        radarSweep: {
          '0%': { transform: 'rotate(0deg)' },
          '100%': { transform: 'rotate(360deg)' }
        }
      }
    },
  },
  plugins: [],
}
