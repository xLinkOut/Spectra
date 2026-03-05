import { useState, useEffect, useRef } from "react";
import { motion, useInView } from "framer-motion";
import { Github, Star, Terminal, RotateCcw } from "lucide-react";
import { staggerContainer, fadeUp, ease } from "../lib/motion";
import { useGithubStars, fmtStars } from "../hooks/useGithubStars";

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
  const stars = useGithubStars();

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
              <Github size={16} />
              Star on GitHub
              {fmtStars(stars) ? (
                <span
                  className="flex items-center gap-0.5 px-1.5 py-0.5 rounded-md text-[11px] font-bold"
                  style={{ backgroundColor: "rgba(255,255,255,0.15)", color: "inherit", opacity: 0.9 }}
                >
                  <Star size={9} fill="currentColor" style={{ opacity: 0.85 }} />
                  {fmtStars(stars)}
                </span>
              ) : (
                <Star size={13} style={{ opacity: 0.6 }} />
              )}
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
