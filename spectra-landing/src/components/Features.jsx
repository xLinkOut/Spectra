import { useRef } from "react";
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
