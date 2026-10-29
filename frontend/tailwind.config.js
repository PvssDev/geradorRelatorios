/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ['"IBM Plex Sans"', "ui-sans-serif", "system-ui", "sans-serif"],
        mono: ['"IBM Plex Mono"', "ui-monospace", "monospace"],
      },
      borderRadius: {
        sm: "calc(0.875rem - 4px)",
        md: "calc(0.875rem - 2px)",
        lg: "0.875rem",
        xl: "calc(0.875rem + 4px)",
        "2xl": "calc(0.875rem + 8px)",
        "3xl": "calc(0.875rem + 12px)",
        "4xl": "calc(0.875rem + 16px)",
      },
      colors: {
        background: "#f8fafc",
        foreground: "#0f172b",
        card: {
          DEFAULT: "#ffffff",
          foreground: "#0f172b",
        },
        popover: {
          DEFAULT: "#ffffff",
          foreground: "#0f172b",
        },
        primary: {
          DEFAULT: "#001630",
          foreground: "#f8fafc",
        },
        secondary: {
          DEFAULT: "#e6f2fe",
          foreground: "#001630",
        },
        muted: {
          DEFAULT: "#dceaf8",
          foreground: "#45556c",
        },
        accent: {
          DEFAULT: "#3b82f6",
          foreground: "#ffffff",
        },
        "accent-2": "#00bada",
        destructive: {
          DEFAULT: "#dc2626",
          foreground: "#ffffff",
        },
        border: "#c9daeb",
        input: "#bdd0e4",
        ring: "#3b82f6",
        navy: "#001630",
        "navy-2": "#0c2842",
        "slate-blue": "#305275",
        nc: "#dc2626",
        "nc-soft": "#fef2f2",
        pa: "#d97708",
        "pa-soft": "#fffbeb",
        ok: "#079669",
        "ok-soft": "#ecfdf5",
        sidebar: {
          DEFAULT: "#001630",
          foreground: "#f8fafc",
          primary: "#3b82f6",
          "primary-foreground": "#ffffff",
          accent: "#0c2842",
          "accent-foreground": "#f8fafc",
          border: "rgba(255, 255, 255, 0.1)",
          ring: "#3b82f6",
        },
      },
      backgroundImage: {
        "navy-gradient": "linear-gradient(160deg, #001630, #0c2842)",
        "brand-gradient": "linear-gradient(135deg, #3b82f6, #00bada)",
      },
      boxShadow: {
        card: "0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.04)",
        elegant: "0 14px 30px -14px rgba(59, 130, 246, 0.6)",
      },
    },
  },
  plugins: [],
};
