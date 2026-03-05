import { motion, useInView } from "framer-motion";
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
