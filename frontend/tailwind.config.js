// tailwind.config.js
module.exports = {
  content: ['./src/**/*.{js,jsx,ts,tsx}', './public/index.html'],
  darkMode: 'class', // or 'media' or 'class'
  theme: {
    extend: {
      colors: {
        primary: '#1f2937',
        secondary: '#4b5563',
        accent: '#10b981',
        background: '#111827',
        foreground: '#f9fafb',
      },
    },
  },
  variants: {
    extend: {},
  },
  plugins: [],
}