/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{html,svelte,js}", "./public/**/*.{html,svelte,js}"],
  theme: {
    extend: {
      height: {
        '90': '90%'
      }
    },
  },
  daisyui: {
    base: false,
    themes: [
      {
        mine: {
          primary: "#02ec88",
          secondary: "#bf95f9",
          accent: "#dca54c",
          neutral: "#282C34",
          "base-100": "#21252B",
          info: "#3ABFF8",
          success: "#36D399",
          warning: "#FBBD23",
          error: "#F87272",
        },
      },
      "dark",
    ],
  },
  plugins: [require("daisyui")],
};
