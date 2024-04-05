/** @type {import('tailwindcss').Config} */
module.exports = {
  mode: 'jit',
  purge: ['./src/**/*.{js,jsx,ts,tsx}', './public/index.html'],
  darkMode: false, // or 'media' or 'class'
  theme: {
    extend: {
      colors: {
        background: '#282c34',
        altBackground: '#4d4d4d',
        alternative: '#5c5c5c',
        textcolor: '#ffffff',
        highlight: '#ffff00',
        snapshotSelected: '#ff0000'
      },
      zIndex: {
        '10': 10,
        '20': 20,
        '30': 30,
        '40': 40,
        '50': 50,
        '9999': 9999,
      }
    }
  },
  variants: {
    extend: {},
  },
  plugins: [],
}
