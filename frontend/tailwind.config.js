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
      }
    },
  },
  plugins: [],
}
