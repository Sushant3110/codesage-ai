/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        background: {
          DEFAULT: '#090D16',
          subtle: '#0E1424',
          card: '#131A2E',
          surface: '#182138',
          hover: '#1E2945',
        },
        border: {
          subtle: '#1C263F',
          muted: '#283556',
          strong: '#3B4C76',
        },
        accent: {
          DEFAULT: '#6366F1', // Indigo
          hover: '#4F46E5',
          light: '#818CF8',
          subtle: 'rgba(99, 102, 241, 0.12)',
        },
        severity: {
          critical: '#EF4444',
          'critical-bg': 'rgba(239, 68, 68, 0.12)',
          high: '#F97316',
          'high-bg': 'rgba(249, 115, 22, 0.12)',
          medium: '#EAB308',
          'medium-bg': 'rgba(234, 179, 8, 0.12)',
          low: '#3B82F6',
          'low-bg': 'rgba(59, 130, 246, 0.12)',
          info: '#64748B',
          'info-bg': 'rgba(100, 116, 139, 0.12)',
        },
      },
      fontFamily: {
        sans: [
          'Inter',
          '-apple-system',
          'BlinkMacSystemFont',
          '"Segoe UI"',
          'Roboto',
          'sans-serif',
        ],
        mono: [
          'JetBrains Mono',
          'Fira Code',
          'ui-monospace',
          'SFMono-Regular',
          'Menlo',
          'Monaco',
          'Consolas',
          'monospace',
        ],
      },
      keyframes: {
        pulseSubtle: {
          '0%, 100%': { opacity: 1 },
          '50%': { opacity: 0.5 },
        },
      },
      animation: {
        'pulse-subtle': 'pulseSubtle 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
    },
  },
  plugins: [],
};
