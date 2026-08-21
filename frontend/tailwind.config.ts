/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#1b1f27",
        mute: "#5b6573",
        line: "#e6e9ee",
        canvas: "#f6f7f9",
        electric: "#2563eb",
        cyan: "#0891b2",
        violet: "#6d28d9",
        signal: "#059669",
      },
      fontFamily: {
        display: ["Fraunces", "serif"],
        sans: ["IBM Plex Sans", "system-ui", "sans-serif"],
      },
      boxShadow: {
        soft: "0 10px 30px rgba(27,31,39,0.06)",
      },
    },
  },
  plugins: [],
};
