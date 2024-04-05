const flowbite = require("flowbite-react/tailwind");

/** @type {import('tailwindcss').Config} */
module.exports = {
  mode: 'jit',
  purge: ['./src/**/*.{js,jsx,ts,tsx}', './public/index.html'],
  darkMode: false, // or 'media' or 'class'
  theme: {
    extend: {
      colors: {
        background: '#282c34',
        altBackground: '#43474F',
        alternative: '#5c5c5c',
        textcolor: '#ffffff',
        highlight: '#ffff00',
        snapshotSelected: '#ff0000',
        offwhite: '#bababa',
      },
      zIndex: {
        '10': 10,
        '20': 20,
        '30': 30,
        '40': 40,
        '50': 50,
        '9998': 9998,
        '9999': 9999,
      }
    }
  },
  variants: {
    extend: {
      spacing: {
        '10vh': '10vh',
        '20vh': '20vh',
        '30vh': '30vh',
        '40vh': '40vh',
        '50vh': '50vh',
        '60vh': '60vh',
        '70vh': '70vh',
        '80vh': '80vh',
        '90vh': '90vh',
      },
    },
  },
  content: [
    flowbite.content(),
  ],
  plugins: [
    function ({ addUtilities }) {
      const newUtilities = {
        '.overflow-y-scroll': {
          'overflow-y': 'scroll',
        },
        '.h-70vh': {
          height: '70vh',
        },
      };

      addUtilities(newUtilities);
    },
    flowbite.plugin(),
  ],
}
