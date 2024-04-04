/** @type {import('tailwindcss').Config} */
module.exports = {
  mode: 'jit',
  purge: ['./src/**/*.{js,jsx,ts,tsx}', './public/index.html'],
  darkMode: false, // or 'media' or 'class'
  theme: {
    extend: {
      colors: {
        background: '#282c34',
        alternative: '#5c5c5c',
        textcolor: '#ffffff',
      }
    }
  },
  variants: {
    extend: {},
  },
  plugins: [],
}
