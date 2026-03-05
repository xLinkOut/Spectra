import os, sys

BASE = os.path.dirname(os.path.abspath(__file__))

files = {}

files["src/components/Navbar.jsx"] = r'''import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Sun, Moon, Github, Star } from "lucide-react";

export default function Navbar({ theme, toggleTheme }) {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <motion.nav
      initial={{ y: -24, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
      className="fixed top-0 left-0 right-0 z-50 transition-all duration-300"
      style={{
        backdropFilter: scrolled ? "blur(16px) saturate(180%)" : "blur(0px)",
        WebkitBackdropFilter: scrolled ? "blur(16px) saturate(180%)" : "blur(0px)",
        backgroundColor: scrolled
          ? theme === "dark"
            ? "rgba(9, 9, 11, 0.85)"
            : "rgba(255, 255, 255, 0.85)"
          : "transparent",
        borderBottom: scrolled ? "1px solid var(--border)" : "1px solid transparent",
        boxShadow: scrolled ? "0 1px 0 var(--border)" : "none",
      }}
    >
      <div className="max-w-5xl mx-auto px-6 h-14 flex items-center justify-between">
        <motion.a
          href="#"
          className="flex items-center gap-2.5 no-underline"
          whileHover={{ opacity: 0.8 }}
          transition={{ duration: 0.15 }}
        >
          <motion.img
            src="/icon.png"
            alt="Spectra"
            className="w-7 h-7 rounded-md"
            whileHover={{ scale: 1.08, rotate: 3 }}
            transition={{ type: "spring", stiffness: 400, damping: 20 }}
          />
          <span
            className="font-semibold text-[15px] tracking-tight"
            style={{ color: "var(--text-primary)" }}
          >
            Spectra
          </span>
        </motion.a>

        <div className="flex items-center gap-1">
          <motion.a
            href="https://github.com/francescogabrieli/Spectra"
            target="_blank"
            rel="noopener noreferrer"
            className="hidden sm:inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium no-underline mr-1"
            style={{
              color: "var(--text-secondary)",
              border: "1px solid var(--border)",
              backgroundColor: "transparent",
            }}
            whileHover={{
              borderColor: "var(--border-hover)",
              backgroundColor: "var(--bg-tertiary)",
              transition: { duration: 0.15 },
            }}
            whileTap={{ scale: 0.97 }}
          >
            <Github size={13} />
            GitHub
            <Star size={10} style={{ opacity: 0.5 }} />
          </motion.a>

          <motion.button
            onClick={toggleTheme}
            className="p-2 rounded-lg cursor-pointer"
            style={{ color: "var(--text-tertiary)", backgroundColor: "transparent", border: "none" }}
            whileHover={{ backgroundColor: "var(--bg-tertiary)", color: "var(--text-primary)" }}
            whileTap={{ scale: 0.9 }}
            transition={{ duration: 0.15 }}
            aria-label="Toggle theme"
          >
            <AnimatePresence mode="wait" initial={false}>
              <motion.div
                key={theme}
                initial={{ opacity: 0, rotate: -90, scale: 0.7 }}
                animate={{ opacity: 1, rotate: 0, scale: 1 }}
                exit={{ opacity: 0, rotate: 90, scale: 0.7 }}
                transition={{ duration: 0.2 }}
              >
                {theme === "dark" ? <Sun size={17} /> : <Moon size={17} />}
              </motion.div>
            </AnimatePresence>
          </motion.button>
        </div>
      </div>
    </motion.nav>
  );
}
'''

files["src/components/Hero.jsx"] = r'''import { useRef } from "react";
import { motion, useMotionValue, useSpring } from "framer-motion";
import { ArrowRight, Github, ChevronRight } from "lucide-react";
import { staggerContainer, fadeUp, ease } from "../lib/motion";

const HEADLINE = ["Know where", "your money", "actually goes."];

const stats = [
  { value: "CSV & PDF", label: "any bank, any format" },
  { value: "100% offline", label: "nothing leaves your device" },
  { value: "6-layer AI", label: "categorization cascade" },
];

function BrowserMockup({ children }) {
  return (
    <div
      className="floating rounded-2xl overflow-hidden"
      style={{
        boxShadow: "var(--screenshot-shadow)",
        border: "1px solid var(--border)",
      }}
    >
      <div
        className="flex items-center gap-2 px-4 py-3"
        style={{
          borderBottom: "1px solid var(--border)",
          backgroundColor: "var(--bg-secondary)",
        }}
      >
        <div className="flex gap-1.5">
          <span className="w-3 h-3 rounded-full" style={{ backgroundColor: "#ff5f57" }} />
          <span className="w-3 h-3 rounded-full" style={{ backgroundColor: "#febc2e" }} />
          <span className="w-3 h-3 rounded-full" style={{ backgroundColor: "#28c840" }} />
        </div>
        <div
          className="flex-1 mx-8 h-[22px] rounded-md flex items-center justify-center text-[11px] select-none"
          style={{
            backgroundColor: "var(--bg-tertiary)",
            border: "1px solid var(--border)",
            color: "var(--text-tertiary)",
          }}
        >
          localhost:8080 · Spectra Dashboard
        </div>
        <div className="w-16" />
      </div>
      <div style={{ backgroundColor: "var(--bg-tertiary)" }}>{children}</div>
    </div>
  );
}

export default function Hero() {
  const sectionRef = useRef(null);
  const mouseX = useMotionValue(typeof window !== "undefined" ? window.innerWidth / 2 : 400);
  const mouseY = useMotionValue(300);
  const springX = useSpring(mouseX, { stiffness: 60, damping: 20 });
  const springY = useSpring(mouseY, { stiffness: 60, damping: 20 });

  const handleMouseMove = (e) => {
    const rect = sectionRef.current?.getBoundingClientRect();
    if (!rect) return;
    mouseX.set(e.clientX - rect.left);
    mouseY.set(e.clientY - rect.top);
  };

  return (
    <section
      ref={sectionRef}
      className="relative min-h-screen flex flex-col items-center justify-start pt-28 pb-0 px-6 overflow-hidden"
      onMouseMove={handleMouseMove}
    >
      <div className="dot-grid absolute inset-0 opacity-50" />

      <motion.div
        className="absolute w-[600px] h-[600px] rounded-full pointer-events-none"
        style={{
          x: springX,
          y: springY,
          translateX: "-50%",
          translateY: "-50%",
          background: "radial-gradient(ellipse, rgba(99,102,241,0.11) 0%, transparent 70%)",
          filter: "blur(40px)",
        }}
      />
      <div
        className="glow-blob absolute top-28 left-1/2 -translate-x-1/2 w-[800px] h-[300px] rounded-full pointer-events-none"
        style={{
          background: "radial-gradient(ellipse, rgba(99,102,241,0.09) 0%, transparent 70%)",
          filter: "blur(60px)",
        }}
      />

      <div className="max-w-3xl mx-auto text-center relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.05 }}
          className="mb-8"
        >
          <motion.div
            className="inline-flex items-center gap-2 pl-1.5 pr-3.5 py-1.5 rounded-full text-xs font-medium cursor-default"
            style={{
              backgroundColor: "var(--bg-tertiary)",
              color: "var(--text-secondary)",
              border: "1px solid var(--border)",
            }}
            whileHover={{ borderColor: "var(--border-hover)", scale: 1.02 }}
            transition={{ duration: 0.2 }}
          >
            <span
              className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[11px] font-semibold"
              style={{
                background: "linear-gradient(135deg, rgba(99,102,241,0.15), rgba(124,58,237,0.15))",
                color: "var(--grad-a)",
                border: "1px solid rgba(99,102,241,0.2)",
              }}
            >
              Open source
            </span>
            Self-hosted · AGPL-3.0
            <ChevronRight size={12} style={{ opacity: 0.5 }} />
          </motion.div>
        </motion.div>

        <motion.h1
          variants={staggerContainer(0.07, 0.1)}
          initial="hidden"
          animate="show"
          className="text-6xl sm:text-7xl md:text-[5.25rem] font-bold tracking-[-0.035em] leading-[1.0] mb-7"
          style={{ color: "var(--text-primary)" }}
        >
          {HEADLINE.map((line, li) => (
            <span key={li} className="block overflow-hidden">
              {line.split(" ").map((word, wi) => (
                <motion.span
                  key={wi}
                  variants={fadeUp}
                  className={`inline-block mr-[0.25em] last:mr-0 ${li === 2 ? "gradient-text-animated" : ""}`}
                >
                  {word}
                </motion.span>
              ))}
            </span>
          ))}
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 20, filter: "blur(6px)" }}
          animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
          transition={{ duration: 0.7, delay: 0.45, ease }}
          className="text-lg sm:text-xl max-w-xl mx-auto mb-10 leading-relaxed"
          style={{ color: "var(--text-secondary)" }}
        >
          Import your bank exports. Get automatic AI categorization. Browse a
          beautiful local dashboard — no credentials, no cloud, no compromises.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.55, ease }}
          className="flex flex-col sm:flex-row items-center justify-center gap-3 mb-16"
        >
          <motion.a
            href="#waitlist"
            className="group inline-flex items-center gap-2 px-7 py-3.5 rounded-xl text-sm font-semibold text-white no-underline"
            style={{
              background: "linear-gradient(135deg, var(--grad-a), var(--grad-b))",
              boxShadow: "0 4px 20px rgba(79,70,229,0.35), inset 0 1px 0 rgba(255,255,255,0.12)",
            }}
            whileHover={{
              scale: 1.04,
              boxShadow: "0 8px 32px rgba(79,70,229,0.5), inset 0 1px 0 rgba(255,255,255,0.12)",
              transition: { type: "spring", stiffness: 400, damping: 20 },
            }}
            whileTap={{ scale: 0.97 }}
          >
            Join the waitlist
            <motion.span
              animate={{ x: [0, 3, 0] }}
              transition={{ duration: 1.5, repeat: Infinity, ease: "easeInOut", repeatDelay: 1 }}
            >
              <ArrowRight size={16} />
            </motion.span>
          </motion.a>

          <motion.a
            href="https://github.com/francescogabrieli/Spectra"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 px-7 py-3.5 rounded-xl text-sm font-medium no-underline"
            style={{
              backgroundColor: "var(--bg-tertiary)",
              color: "var(--text-primary)",
              border: "1px solid var(--border)",
            }}
            whileHover={{
              borderColor: "var(--border-hover)",
              backgroundColor: "var(--card-bg)",
              boxShadow: "var(--card-shadow-hover)",
              transition: { duration: 0.2 },
            }}
            whileTap={{ scale: 0.97 }}
          >
            <Github size={16} />
            View on GitHub
          </motion.a>
        </motion.div>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 1, delay: 0.7 }}
          className="flex items-center justify-center gap-6 sm:gap-10 flex-wrap"
        >
          {stats.map((s, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.75 + i * 0.08, duration: 0.5, ease }}
              className="flex flex-col items-center gap-0.5"
            >
              <span className="text-[13px] font-semibold tracking-tight" style={{ color: "var(--text-primary)" }}>
                {s.value}
              </span>
              <span className="text-[11px]" style={{ color: "var(--text-tertiary)" }}>
                {s.label}
              </span>
            </motion.div>
          ))}
        </motion.div>
      </div>

      <motion.div
        initial={{ opacity: 0, y: 80, scale: 0.94, filter: "blur(12px)" }}
        animate={{ opacity: 1, y: 0, scale: 1, filter: "blur(0px)" }}
        transition={{ duration: 1.1, delay: 0.6, ease: [0.16, 1, 0.3, 1] }}
        className="w-full max-w-5xl mx-auto mt-16 relative z-10"
      >
        <BrowserMockup>
          <img
            src="/dashboard.png"
            alt="Spectra Dashboard"
            className="w-full h-auto block"
            style={{ maxHeight: "540px", objectFit: "cover", objectPosition: "top" }}
          />
        </BrowserMockup>
        <div
          className="absolute bottom-0 left-0 right-0 h-48 pointer-events-none"
          style={{ background: "linear-gradient(to bottom, transparent, var(--bg))" }}
        />
      </motion.div>
    </section>
  );
}
'''

files["src/components/HowItWorks.jsx"] = r'''import { useRef } from "react";
import { motion, useInView } from "framer-motion";
import { Upload, Cpu, BarChart2 } from "lucide-react";
import { staggerContainer, fadeUp, ease } from "../lib/motion";

const steps = [
  {
    n: "01",
    icon: Upload,
    title: "Drop your export",
    body: "Download your bank statement as CSV or PDF — any bank, any format. No Open Banking, no login, no API keys.",
    accent: "#6366f1",
  },
  {
    n: "02",
    icon: Cpu,
    title: "Let it categorize",
    body: "A 6-layer cascade handles it: merchant memory, fuzzy matching, keyword rules, ML classifier, and optional AI fallback.",
    accent: "#8b5cf6",
  },
  {
    n: "03",
    icon: BarChart2,
    title: "See the full picture",
    body: "Budgets, trends, recurring detection, multi-currency FX — everything in a clean local dashboard at localhost:8080.",
    accent: "#a78bfa",
  },
];

function StepCard({ step, delay }) {
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, margin: "-60px" });

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 40, filter: "blur(8px)" }}
      animate={inView ? { opacity: 1, y: 0, filter: "blur(0px)" } : {}}
      transition={{ duration: 0.65, delay, ease }}
      className="relative p-6 rounded-2xl gradient-border group cursor-default"
      whileHover={{ y: -8, transition: { type: "spring", stiffness: 350, damping: 22 } }}
      style={{ backgroundColor: "var(--card-bg)", border: "1px solid var(--border)" }}
    >
      <div
        className="text-[5rem] font-black mb-2 select-none leading-none tracking-[-0.04em]"
        style={{ color: "var(--border)", transition: "color 0.25s" }}
      >
        {step.n}
      </div>

      <motion.div
        className="w-10 h-10 rounded-xl flex items-center justify-center mb-5"
        style={{
          background: `linear-gradient(135deg, ${step.accent}22, ${step.accent}44)`,
          border: `1px solid ${step.accent}40`,
        }}
        whileHover={{ scale: 1.12, rotate: 4 }}
        transition={{ type: "spring", stiffness: 400, damping: 18 }}
      >
        <step.icon size={19} style={{ color: step.accent }} />
      </motion.div>

      <h3 className="text-[15px] font-semibold mb-2.5 tracking-tight" style={{ color: "var(--text-primary)" }}>
        {step.title}
      </h3>
      <p className="text-sm leading-relaxed" style={{ color: "var(--text-secondary)" }}>
        {step.body}
      </p>

      <motion.div
        className="absolute bottom-0 left-6 right-6 h-px rounded-full"
        initial={{ scaleX: 0, opacity: 0 }}
        whileHover={{ scaleX: 1, opacity: 1 }}
        style={{
          background: `linear-gradient(90deg, transparent, ${step.accent}60, transparent)`,
          transformOrigin: "left",
        }}
        transition={{ duration: 0.4 }}
      />
    </motion.div>
  );
}

export default function HowItWorks() {
  const headerRef = useRef(null);
  const headerInView = useInView(headerRef, { once: true, margin: "-80px" });
  const lineRef = useRef(null);
  const lineInView = useInView(lineRef, { once: true, margin: "-40px" });

  return (
    <section className="py-28 px-6" style={{ backgroundColor: "var(--bg-secondary)" }}>
      <div className="max-w-5xl mx-auto">
        <motion.div
          ref={headerRef}
          variants={staggerContainer(0.1)}
          initial="hidden"
          animate={headerInView ? "show" : "hidden"}
          className="mb-16"
        >
          <motion.p variants={fadeUp} className="text-xs font-semibold tracking-widest uppercase mb-3" style={{ color: "var(--text-tertiary)" }}>
            How it works
          </motion.p>
          <motion.h2 variants={fadeUp} className="text-4xl sm:text-5xl font-bold tracking-[-0.03em] leading-tight" style={{ color: "var(--text-primary)" }}>
            Three steps.
            <br />
            <span className="gradient-text">Zero compromises.</span>
          </motion.h2>
        </motion.div>

        <div ref={lineRef} className="relative">
          <div className="hidden md:block absolute top-[2.8rem] left-[calc(33.33%+12px)] right-[calc(33.33%+12px)] h-px overflow-hidden">
            <motion.div
              className="h-full"
              style={{ background: "linear-gradient(90deg, var(--grad-a), var(--grad-b))" }}
              initial={{ scaleX: 0, transformOrigin: "left" }}
              animate={lineInView ? { scaleX: 1 } : {}}
              transition={{ duration: 0.8, delay: 0.5, ease }}
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 relative z-10">
            {steps.map((step, i) => (
              <StepCard key={step.n} step={step} delay={i * 0.14} />
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
'''

files["src/components/Features.jsx"] = r'''import { useRef } from "react";
import { motion, useMotionValue, useTransform, useInView } from "framer-motion";
import { Shield, HardDrive, Zap, Globe, RefreshCw, Lock } from "lucide-react";
import { staggerContainer, fadeUp, ease } from "../lib/motion";

const features = [
  { icon: Shield, title: "No bank credentials", body: "You export files manually. Spectra never touches your bank — no Open Banking, no login, no API keys to get started.", accent: "#6366f1" },
  { icon: HardDrive, title: "Local-first, always", body: "SQLite on your machine. The dashboard runs at localhost. Nothing leaves your device unless you configure Sheets sync.", accent: "#8b5cf6" },
  { icon: Zap, title: "6-layer categorization", body: "User overrides → merchant memory → fuzzy match → keyword rules → ML → AI. Gets smarter with every import.", accent: "#ec4899" },
  { icon: Globe, title: "Multi-currency", body: "Historical ECB rates via Frankfurter API. Auto-converts any currency with no key required.", accent: "#f59e0b" },
  { icon: RefreshCw, title: "Recurring detection", body: "Automatically identifies subscriptions, salary and rent from your transaction patterns. Flags them for review.", accent: "#10b981" },
  { icon: Lock, title: "Fully open source", body: "AGPL-3.0. Every line auditable. No telemetry, no analytics, no surprise network calls. Fork it, own it.", accent: "#14b8a6" },
];

function FeatureCard({ feature, i }) {
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, margin: "-50px" });
  const mouseX = useMotionValue(0);
  const mouseY = useMotionValue(0);

  const handleMouseMove = (e) => {
    const rect = e.currentTarget.getBoundingClientRect();
    mouseX.set(e.clientX - rect.left);
    mouseY.set(e.clientY - rect.top);
  };

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 36, filter: "blur(8px)" }}
      animate={inView ? { opacity: 1, y: 0, filter: "blur(0px)" } : {}}
      transition={{ duration: 0.6, delay: i * 0.07, ease }}
      className="relative p-5 rounded-2xl group overflow-hidden cursor-default"
      style={{ backgroundColor: "var(--card-bg)", border: "1px solid var(--border)" }}
      whileHover={{
        y: -5,
        borderColor: `${feature.accent}50`,
        transition: { type: "spring", stiffness: 350, damping: 25 },
      }}
      onMouseMove={handleMouseMove}
      onMouseLeave={() => { mouseX.set(0); mouseY.set(0); }}
    >
      <motion.div
        className="absolute inset-0 rounded-2xl opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity duration-300"
        style={{
          background: useTransform(
            [mouseX, mouseY],
            ([x, y]) => `radial-gradient(220px circle at ${x}px ${y}px, ${feature.accent}14, transparent 70%)`
          ),
        }}
      />
      <div
        className="absolute top-0 left-0 w-32 h-32 rounded-full pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity duration-500"
        style={{
          background: `radial-gradient(ellipse, ${feature.accent}18 0%, transparent 65%)`,
          filter: "blur(20px)",
          transform: "translate(-35%, -35%)",
        }}
      />
      <motion.div
        className="w-9 h-9 rounded-xl flex items-center justify-center mb-4 relative z-10"
        style={{ backgroundColor: `${feature.accent}14`, border: `1px solid ${feature.accent}28` }}
        whileHover={{ scale: 1.1, rotate: 5 }}
        transition={{ type: "spring", stiffness: 400, damping: 18 }}
      >
        <feature.icon size={17} style={{ color: feature.accent }} />
      </motion.div>
      <h3 className="text-[15px] font-semibold mb-2 leading-snug relative z-10" style={{ color: "var(--text-primary)" }}>
        {feature.title}
      </h3>
      <p className="text-sm leading-relaxed relative z-10" style={{ color: "var(--text-secondary)" }}>
        {feature.body}
      </p>
    </motion.div>
  );
}

export default function Features() {
  const headerRef = useRef(null);
  const headerInView = useInView(headerRef, { once: true, margin: "-80px" });

  return (
    <section className="py-28 px-6" style={{ backgroundColor: "var(--bg)" }}>
      <div className="max-w-5xl mx-auto">
        <motion.div
          ref={headerRef}
          variants={staggerContainer(0.1)}
          initial="hidden"
          animate={headerInView ? "show" : "hidden"}
          className="mb-16"
        >
          <motion.p variants={fadeUp} className="text-xs font-semibold tracking-widest uppercase mb-3" style={{ color: "var(--text-tertiary)" }}>
            Why Spectra
          </motion.p>
          <motion.h2 variants={fadeUp} className="text-4xl sm:text-5xl font-bold tracking-[-0.03em] leading-tight" style={{ color: "var(--text-primary)" }}>
            Built different.
            <br />
            <span className="gradient-text">Privacy by design.</span>
          </motion.h2>
        </motion.div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {features.map((f, i) => (
            <FeatureCard key={f.title} feature={f} i={i} />
          ))}
        </div>
      </div>
    </section>
  );
}
'''

files["src/components/Waitlist.jsx"] = r'''import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence, useInView } from "framer-motion";
import { ArrowRight, Check, Loader2, Sparkles } from "lucide-react";
import { staggerContainer, fadeUp, ease } from "../lib/motion";

const STORAGE_KEY = "spectra-waitlist";

function getWaitlistData() {
  try {
    const d = JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]");
    return Array.isArray(d) ? d : [];
  } catch { return []; }
}

function useCountUp(target, duration = 1400) {
  const [val, setVal] = useState(0);
  const started = useRef(false);
  useEffect(() => {
    if (!target || started.current) return;
    started.current = true;
    const start = Date.now();
    const tick = () => {
      const t = Math.min((Date.now() - start) / duration, 1);
      const eased = 1 - Math.pow(1 - t, 3);
      setVal(Math.floor(eased * target));
      if (t < 1) requestAnimationFrame(tick);
      else setVal(target);
    };
    requestAnimationFrame(tick);
  }, [target, duration]);
  return val;
}

export default function Waitlist() {
  const [email, setEmail] = useState("");
  const [status, setStatus] = useState("idle");
  const [count, setCount] = useState(0);
  const [joined, setJoined] = useState(false);
  const animatedCount = useCountUp(count);
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, margin: "-80px" });

  useEffect(() => {
    setCount(getWaitlistData().length);
    if (localStorage.getItem("spectra-waitlist-joined")) setJoined(true);
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email || status === "loading") return;
    const t = email.trim().toLowerCase();
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(t)) { setStatus("error"); return; }
    setStatus("loading");
    await new Promise((r) => setTimeout(r, 900));
    const existing = getWaitlistData();
    if (!existing.some((x) => x.email === t)) {
      existing.push({ email: t, timestamp: new Date().toISOString(), source: "landing" });
      localStorage.setItem(STORAGE_KEY, JSON.stringify(existing));
      setCount(existing.length);
    }
    localStorage.setItem("spectra-waitlist-joined", t);
    setStatus("success");
    setJoined(true);
    setEmail("");
  };

  return (
    <section id="waitlist" ref={ref} className="py-32 px-6 relative overflow-hidden" style={{ backgroundColor: "var(--bg-secondary)" }}>
      <div className="absolute inset-0 pointer-events-none" style={{ background: "radial-gradient(ellipse 80% 50% at 50% 110%, rgba(99,102,241,0.07) 0%, transparent 65%)" }} />
      <div className="glow-blob absolute -top-32 right-0 w-[500px] h-[500px] rounded-full pointer-events-none" style={{ background: "radial-gradient(ellipse, rgba(124,58,237,0.06) 0%, transparent 70%)", filter: "blur(60px)", animationDelay: "3s" }} />

      <div className="max-w-xl mx-auto text-center relative z-10">
        <motion.div variants={staggerContainer(0.1)} initial="hidden" animate={inView ? "show" : "hidden"}>
          <motion.div variants={fadeUp} className="mb-8">
            <motion.div
              className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full text-xs font-semibold"
              style={{ background: "linear-gradient(135deg, rgba(99,102,241,0.1), rgba(124,58,237,0.1))", color: "var(--grad-a)", border: "1px solid rgba(99,102,241,0.2)" }}
              whileHover={{ scale: 1.03 }}
              transition={{ type: "spring", stiffness: 400, damping: 20 }}
            >
              <motion.span animate={{ rotate: [0, 15, -10, 0] }} transition={{ duration: 2, repeat: Infinity, repeatDelay: 4 }}>
                <Sparkles size={12} />
              </motion.span>
              Coming soon — Hosted web app
            </motion.div>
          </motion.div>

          <motion.h2 variants={fadeUp} className="text-4xl sm:text-5xl font-bold tracking-[-0.03em] mb-5 leading-tight" style={{ color: "var(--text-primary)" }}>
            Spectra,
            <br />
            <span className="gradient-text-animated">without the setup.</span>
          </motion.h2>

          <motion.p variants={fadeUp} className="text-base sm:text-lg max-w-sm mx-auto mb-10 leading-relaxed" style={{ color: "var(--text-secondary)" }}>
            Same privacy-first approach. Zero terminal required. Leave your email and be first in line.
          </motion.p>
        </motion.div>

        <AnimatePresence mode="wait">
          {joined ? (
            <motion.div key="success" initial={{ opacity: 0, scale: 0.85, y: 16 }} animate={{ opacity: 1, scale: 1, y: 0 }} exit={{ opacity: 0 }} transition={{ type: "spring", stiffness: 280, damping: 22 }} className="flex flex-col items-center gap-4 py-4">
              <motion.div
                className="w-16 h-16 rounded-2xl flex items-center justify-center"
                style={{ background: "linear-gradient(135deg, var(--grad-a), var(--grad-b))", boxShadow: "0 8px 32px rgba(99,102,241,0.35)" }}
                initial={{ scale: 0, rotate: -20 }}
                animate={{ scale: 1, rotate: 0 }}
                transition={{ type: "spring", stiffness: 300, damping: 20, delay: 0.1 }}
              >
                <Check size={28} color="white" strokeWidth={2.5} />
              </motion.div>
              <div>
                <motion.p className="text-lg font-semibold mb-1" style={{ color: "var(--text-primary)" }} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
                  You&apos;re on the list!
                </motion.p>
                <motion.p className="text-sm" style={{ color: "var(--text-secondary)" }} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
                  We&apos;ll reach out when the hosted version launches.
                </motion.p>
              </div>
            </motion.div>
          ) : (
            <motion.form key="form" onSubmit={handleSubmit} initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} transition={{ duration: 0.4 }} className="flex flex-col sm:flex-row gap-2.5 max-w-md mx-auto">
              <motion.input
                type="email" value={email}
                onChange={(e) => { setEmail(e.target.value); if (status === "error") setStatus("idle"); }}
                placeholder="you@email.com"
                className="flex-1 px-4 py-3 rounded-xl text-sm outline-none"
                style={{ backgroundColor: "var(--card-bg)", color: "var(--text-primary)", border: `1.5px solid ${status === "error" ? "#ef4444" : "var(--border)"}`, transition: "border-color 0.2s, box-shadow 0.2s" }}
                whileFocus={{
                  borderColor: status === "error" ? "#ef4444" : "var(--grad-a)",
                  boxShadow: status === "error" ? "0 0 0 3px rgba(239,68,68,0.1)" : "0 0 0 3px rgba(99,102,241,0.1)",
                }}
              />
              <motion.button
                type="submit" disabled={status === "loading"}
                className="inline-flex items-center justify-center gap-2 px-6 py-3 rounded-xl text-sm font-semibold text-white whitespace-nowrap cursor-pointer"
                style={{ background: "linear-gradient(135deg, var(--grad-a), var(--grad-b))", border: "none", boxShadow: "0 4px 16px rgba(99,102,241,0.3)", opacity: status === "loading" ? 0.7 : 1 }}
                whileHover={{ scale: 1.03, boxShadow: "0 6px 24px rgba(99,102,241,0.45)", transition: { type: "spring", stiffness: 400, damping: 18 } }}
                whileTap={{ scale: 0.97 }}
              >
                <AnimatePresence mode="wait" initial={false}>
                  {status === "loading" ? (
                    <motion.span key="loading" initial={{ opacity: 0, scale: 0.8 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0, scale: 0.8 }}>
                      <Loader2 size={16} className="animate-spin" />
                    </motion.span>
                  ) : (
                    <motion.span key="submit" className="flex items-center gap-2" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                      Notify me <ArrowRight size={15} />
                    </motion.span>
                  )}
                </AnimatePresence>
              </motion.button>
            </motion.form>
          )}
        </AnimatePresence>

        <AnimatePresence>
          {status === "error" && (
            <motion.p initial={{ opacity: 0, y: -4 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} className="text-xs mt-2" style={{ color: "#ef4444" }}>
              Please enter a valid email address.
            </motion.p>
          )}
        </AnimatePresence>

        <AnimatePresence>
          {count > 0 && (
            <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.6, duration: 0.5 }} className="flex items-center justify-center gap-2 mt-7">
              <div className="flex -space-x-2">
                {[...Array(3)].map((_, idx) => (
                  <div key={idx} className="w-6 h-6 rounded-full flex items-center justify-center text-[9px] font-bold text-white" style={{ background: `linear-gradient(135deg, hsl(${220 + idx * 30}, 70%, 55%), hsl(${250 + idx * 30}, 70%, 60%))`, border: "2px solid var(--bg-secondary)" }}>
                    {["F","A","M"][idx]}
                  </div>
                ))}
              </div>
              <span className="text-sm" style={{ color: "var(--text-tertiary)" }}>
                <strong style={{ color: "var(--text-secondary)" }}>{animatedCount}</strong>{" "}
                {count === 1 ? "person" : "people"} already waiting
              </span>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </section>
  );
}
'''

files["src/components/GithubCTA.jsx"] = r'''import { useState, useEffect, useRef } from "react";
import { motion, useInView } from "framer-motion";
import { Github, Star, Terminal, RotateCcw } from "lucide-react";
import { staggerContainer, fadeUp, ease } from "../lib/motion";

const LINES = [
  { prompt: "~", cmd: "git clone https://github.com/francescogabrieli/Spectra", out: null, outColor: null },
  { prompt: "~/Spectra", cmd: "pip install -r requirements.txt", out: null, outColor: null },
  { prompt: "~/Spectra", cmd: "python -m spectra --serve", out: "✓  Spectra running at http://localhost:8080", outColor: "#3fb950" },
];

function useTypewriter(lines, active) {
  const [state, setState] = useState({ lineIdx: 0, charIdx: 0, showOut: false, done: false });
  const timerRef = useRef(null);

  useEffect(() => {
    if (!active) return;
    setState({ lineIdx: 0, charIdx: 0, showOut: false, done: false });
  }, [active]);

  useEffect(() => {
    if (!active || state.done) return;
    const line = lines[state.lineIdx];
    if (!line) { setState((s) => ({ ...s, done: true })); return; }

    if (state.charIdx < line.cmd.length) {
      timerRef.current = setTimeout(() => setState((s) => ({ ...s, charIdx: s.charIdx + 1 })), 24 + Math.random() * 16);
    } else if (line.out && !state.showOut) {
      timerRef.current = setTimeout(() => setState((s) => ({ ...s, showOut: true })), 280);
    } else {
      const next = state.lineIdx + 1;
      if (next < lines.length) {
        timerRef.current = setTimeout(() => setState({ lineIdx: next, charIdx: 0, showOut: false, done: false }), 560);
      } else {
        timerRef.current = setTimeout(() => setState((s) => ({ ...s, done: true })), 400);
      }
    }
    return () => clearTimeout(timerRef.current);
  }, [active, state, lines]);

  const replay = () => setState({ lineIdx: 0, charIdx: 0, showOut: false, done: false });
  return { state, replay };
}

function TerminalWindow() {
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, margin: "-80px" });
  const { state, replay } = useTypewriter(LINES, inView);

  return (
    <div ref={ref} className="rounded-2xl overflow-hidden font-mono text-sm select-none" style={{ backgroundColor: "#0d1117", border: "1px solid #30363d", boxShadow: "0 24px 80px rgba(0,0,0,0.45), 0 4px 16px rgba(0,0,0,0.3)" }}>
      <div className="flex items-center justify-between px-4 py-2.5" style={{ borderBottom: "1px solid #21262d", backgroundColor: "#161b22" }}>
        <div className="flex items-center gap-2">
          <div className="flex gap-1.5">
            <span className="w-3 h-3 rounded-full" style={{ backgroundColor: "#ff5f57" }} />
            <span className="w-3 h-3 rounded-full" style={{ backgroundColor: "#febc2e" }} />
            <span className="w-3 h-3 rounded-full" style={{ backgroundColor: "#28c840" }} />
          </div>
          <div className="flex items-center gap-1.5 ml-3">
            <Terminal size={11} style={{ color: "#8b949e" }} />
            <span style={{ color: "#8b949e", fontSize: "11px" }}>zsh — spectra setup</span>
          </div>
        </div>
        {state.done && (
          <motion.button initial={{ opacity: 0 }} animate={{ opacity: 1 }} onClick={replay} className="cursor-pointer" style={{ background: "none", border: "none", color: "#8b949e", padding: 0 }} whileHover={{ color: "#c9d1d9" }} title="Replay">
            <RotateCcw size={13} />
          </motion.button>
        )}
      </div>
      <div className="p-5 space-y-1.5 min-h-[172px]">
        {LINES.map((line, idx) => {
          if (idx > state.lineIdx) return null;
          const isCurrent = idx === state.lineIdx && !state.done;
          const isFinished = idx < state.lineIdx || state.done;
          const displayCmd = isCurrent ? line.cmd.slice(0, state.charIdx) : line.cmd;
          const showOut = isFinished ? !!line.out : (idx === state.lineIdx && state.showOut && !!line.out);
          return (
            <div key={idx}>
              <div className="flex items-baseline gap-2 flex-wrap leading-6">
                <span style={{ color: "#3fb950", fontSize: "13px" }}>{line.prompt}</span>
                <span style={{ color: "#58a6ff", fontSize: "13px" }}>$</span>
                <span style={{ color: "#e6edf3", fontSize: "13px" }}>
                  {displayCmd}
                  {isCurrent && <span className="cursor-blink inline-block w-[7px] h-[14px] ml-[1px] align-text-bottom rounded-sm" style={{ backgroundColor: "#c9d1d9" }} />}
                </span>
              </div>
              {showOut && (
                <motion.div initial={{ opacity: 0, y: 4 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3 }} style={{ color: line.outColor || "#3fb950", fontSize: "13px", paddingLeft: "0.5rem" }}>
                  {line.out}
                </motion.div>
              )}
            </div>
          );
        })}
        {state.done && (
          <div className="flex items-baseline gap-2 leading-6">
            <span style={{ color: "#3fb950", fontSize: "13px" }}>~/Spectra</span>
            <span style={{ color: "#58a6ff", fontSize: "13px" }}>$</span>
            <span className="cursor-blink inline-block w-[7px] h-[14px] align-text-bottom rounded-sm" style={{ backgroundColor: "#c9d1d9" }} />
          </div>
        )}
      </div>
    </div>
  );
}

export default function GithubCTA() {
  const leftRef = useRef(null);
  const leftInView = useInView(leftRef, { once: true, margin: "-80px" });

  return (
    <section className="py-28 px-6" style={{ backgroundColor: "var(--bg)" }}>
      <div className="max-w-5xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-14 items-center">
        <motion.div ref={leftRef} variants={staggerContainer(0.1)} initial="hidden" animate={leftInView ? "show" : "hidden"}>
          <motion.p variants={fadeUp} className="text-xs font-semibold tracking-widest uppercase mb-3" style={{ color: "var(--text-tertiary)" }}>
            Get started now
          </motion.p>
          <motion.h2 variants={fadeUp} className="text-4xl sm:text-5xl font-bold tracking-[-0.03em] mb-5 leading-tight" style={{ color: "var(--text-primary)" }}>
            Ready in
            <br />
            <span className="gradient-text">60 seconds.</span>
          </motion.h2>
          <motion.p variants={fadeUp} className="text-base mb-8 leading-relaxed max-w-sm" style={{ color: "var(--text-secondary)" }}>
            Free, open source, one Python command. No cloud account, no subscription, no vendor lock-in. You own your data, forever.
          </motion.p>
          <motion.div variants={fadeUp} className="flex flex-col sm:flex-row gap-3">
            <motion.a
              href="https://github.com/francescogabrieli/Spectra" target="_blank" rel="noopener noreferrer"
              className="inline-flex items-center gap-2 px-6 py-3 rounded-xl text-sm font-semibold no-underline"
              style={{ backgroundColor: "var(--text-primary)", color: "var(--bg)", border: "none" }}
              whileHover={{ scale: 1.03, opacity: 0.9, transition: { type: "spring", stiffness: 400, damping: 20 } }}
              whileTap={{ scale: 0.97 }}
            >
              <Github size={16} /> Star on GitHub <Star size={13} style={{ opacity: 0.6 }} />
            </motion.a>
            <motion.a
              href="https://github.com/francescogabrieli/Spectra#quick-start" target="_blank" rel="noopener noreferrer"
              className="inline-flex items-center gap-2 px-6 py-3 rounded-xl text-sm font-medium no-underline"
              style={{ color: "var(--text-secondary)", border: "1px solid var(--border)", backgroundColor: "transparent" }}
              whileHover={{ borderColor: "var(--border-hover)", backgroundColor: "var(--bg-tertiary)", transition: { duration: 0.2 } }}
              whileTap={{ scale: 0.97 }}
            >
              Read the docs
            </motion.a>
          </motion.div>
        </motion.div>
        <motion.div
          initial={{ opacity: 0, x: 40, filter: "blur(8px)" }}
          whileInView={{ opacity: 1, x: 0, filter: "blur(0px)" }}
          viewport={{ once: true, margin: "-80px" }}
          transition={{ duration: 0.7, delay: 0.15, ease }}
        >
          <TerminalWindow />
        </motion.div>
      </div>
    </section>
  );
}
'''

files["src/components/Footer.jsx"] = r'''import { motion, useInView } from "framer-motion";
import { useRef } from "react";
import { Github, Heart } from "lucide-react";

const links = [
  { label: "GitHub", href: "https://github.com/francescogabrieli/Spectra" },
  { label: "Issues", href: "https://github.com/francescogabrieli/Spectra/issues" },
  { label: "License", href: "https://github.com/francescogabrieli/Spectra/blob/main/LICENSE" },
];

export default function Footer() {
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, margin: "-40px" });

  return (
    <motion.footer
      ref={ref}
      initial={{ opacity: 0, y: 16 }}
      animate={inView ? { opacity: 1, y: 0 } : {}}
      transition={{ duration: 0.6 }}
      className="py-10 px-6"
      style={{ borderTop: "1px solid var(--border)" }}
    >
      <div className="max-w-5xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-2.5">
          <img src="/icon.png" alt="Spectra" className="w-5 h-5 rounded-md opacity-70" />
          <span className="text-sm" style={{ color: "var(--text-tertiary)" }}>
            Spectra — Your finances, your control.
          </span>
        </div>
        <div className="flex items-center gap-5 text-xs">
          {links.map((l) => (
            <motion.a key={l.label} href={l.href} target="_blank" rel="noopener noreferrer" className="no-underline" style={{ color: "var(--text-tertiary)" }} whileHover={{ color: "var(--text-secondary)" }} transition={{ duration: 0.15 }}>
              {l.label}
            </motion.a>
          ))}
          <span className="flex items-center gap-1" style={{ color: "var(--text-tertiary)" }}>
            Made with <Heart size={11} style={{ color: "#ec4899" }} fill="#ec4899" /> 2026
          </span>
        </div>
      </div>
    </motion.footer>
  );
}
'''

for path, content in files.items():
    full = os.path.join(BASE, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as f:
        f.write(content)
    print(f"OK {path}")

print("All files written.")
