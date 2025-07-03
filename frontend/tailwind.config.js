const defaultTheme = require("tailwindcss/defaultTheme");

module.exports = {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        border: "hsl(var(--border))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        // 필요하면 card·accent 등도 그대로 추가
      },
      fontFamily: {
        "abhaya-libre": ['"Abhaya Libre"', ...defaultTheme.fontFamily.serif],
        paperlogy: ['"Inter"', ...defaultTheme.fontFamily.sans],
      },
    },
  },
  plugins: [],
};
