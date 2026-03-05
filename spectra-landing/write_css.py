import os

css = r"""@import "tailwindcss";

@custom-variant dark (&:where(.dark, .dark *));

@theme {
  --font-sans: "Inter", system-ui, sans-serif;
  --color-primary-500: #6366f1;
  --color-primary-600: #4f46e5;
  --color-primary-700: #4338ca;
}

html {
  font-family: var(--font-sans);
  scroll-behavior: smooth;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

body {
  min-height: 100vh;
  transition: background-color 0.3s ease, color 0.3s ease;
  overflow-x: hidden;
}

:root {
  --bg: #ffffff;
  --bg-secondary: #f9fafb;
  --bg-tertiary: #f3f4f6;
  --text-primary: #0f0f10;
  --text-secondary: #4b5563;
  --text-tertiary: #9ca3af;
  --border: #e5e7eb;
  --border-hover: #d1d5db;
  --card-bg: #ffffff;
  --card-shadow: 0 1px 2px rgba(0,0,0,0.04), 0 2px 6px rgba(0,0,0,0.04);
  --card-shadow-hover: 0 8px 32px rgba(0,0,0,0.1), 0 2px 8px rgba(0,0,0,0.04);
  --screenshot-shadow: 0 40px 100px rgba(0,0,0,0.15), 0 8px 24px rgba(0,0,0,0.06);
  --grad-a: #4f46e5;
  --grad-b: #7c3aed;
}

.dark {
  --bg: #09090b;
  --bg-secondary: #111113;
  --bg-tertiary: #18181b;
  --text-primary: #fafafa;
  --text-secondary: #a1a1aa;
  --text-tertiary: #52525b;
  --border: #27272a;
  --border-hover: #3f3f46;
  --card-bg: #111113;
  --card-shadow: 0 1px 2px rgba(0,0,0,0.4), 0 2px 8px rgba(0,0,0,0.3);
  --card-shadow-hover: 0 8px 32px rgba(0,0,0,0.6), 0 2px 8px rgba(0,0,0,0.4);
  --screenshot-shadow: 0 40px 100px rgba(0,0,0,0.7), 0 8px 24px rgba(0,0,0,0.5);
  --grad-a: #818cf8;
  --grad-b: #a78bfa;
}

body { background-color: var(--bg); color: var(--text-primary); }

.gradient-text {
  background: linear-gradient(135deg, var(--grad-a) 0%, var(--grad-b) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

@keyframes shimmer {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

.gradient-text-animated {
  background: linear-gradient(135deg, #4f46e5, #7c3aed, #6366f1, #4f46e5);
  background-size: 300% 300%;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: shimmer 8s ease infinite;
}

.dark .gradient-text-animated {
  background: linear-gradient(135deg, #818cf8, #a78bfa, #818cf8, #c4b5fd);
  background-size: 300% 300%;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: shimmer 8s ease infinite;
}

.dot-grid {
  background-image: radial-gradient(circle, var(--border) 1px, transparent 1px);
  background-size: 32px 32px;
}

@keyframes pulse-glow {
  0%, 100% { opacity: 0.25; }
  50% { opacity: 0.55; }
}

.glow-blob { animation: pulse-glow 6s ease-in-out infinite; }

@keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0; } }
.cursor-blink { animation: blink 1s step-end infinite; }

::selection { background-color: rgba(99,102,241,0.15); color: var(--text-primary); }
"""

target = os.path.join(os.path.dirname(__file__), "src", "index.css")
with open(target, "w") as f:
    f.write(css)
print("CSS written OK")
