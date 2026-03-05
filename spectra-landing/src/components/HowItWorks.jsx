import { useRef } from "react";
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
