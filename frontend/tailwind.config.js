module.exports = {
  presets: [require('frappe-ui/src/utils/tailwind.config')],
  content: [
    './index.html',
    './src/**/*.{vue,js,ts,jsx,tsx}',
    './node_modules/frappe-ui/src/components/**/*.{vue,js,ts,jsx,tsx}',
    '../node_modules/frappe-ui/src/components/**/*.{vue,js,ts,jsx,tsx}',
  ],
  safelist: [
    { pattern: /!(text|bg)-/, variants: ['hover', 'active'] },
    { pattern: /^grid-cols-/ },
  ],
  theme: {
    extend: {
      colors: {
        // gray: {
        //   50: '#fff2e6',
        //   100: '#ffe6cc',
        //   200: '#ffd9b3',
        //   300: '#ffbf80',
        //   400: '#ffbf80',
        //   500: '#ffb366',
        //   600: '#ffa64d',
        //   700: '#ff9933',
        //   800: '#ff8c1a',
        //   900: '#ff8000'
        // }

        // gray: {
        //   50: '#f2e6ff',
        //   100: '#e6ccff',
        //   200: '#d9b3ff',
        //   300: '#cc99ff',
        //   400: '#bf80ff',
        //   500: '#b366ff',
        //   600: '#a64dff',
        //   700: '#9933ff',
        //   800: '#8c1aff',
        //   900: '#8000ff'
        // }
        // gray: { //mGrant
        //   50:  '#F9E5E9',  // Lightest shade
        //   100: '#F2CCD4',
        //   200: '#E599A9',
        //   300: '#D9667F',
        //   400: '#CC3354',
        //   500: '#BF002A',  // Midway between base and light
        //   600: '#B30026',  // Slightly lighter than base
        //   700: '#A60022',
        //   800: '#99001E',
        //   900: '#A01236'   // Darkest shade as provided
        // }
      }
    },
  },
  plugins: [],
}
