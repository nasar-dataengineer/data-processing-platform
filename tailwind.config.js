export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      boxShadow: {
        glass: "0 8px 32px rgba(14, 17, 34, 0.18)",
      },
      backgroundImage: {
        gradientRadial: "radial-gradient(var(--tw-gradient-stops))",
      },
    },
  },
  plugins: [],
};
