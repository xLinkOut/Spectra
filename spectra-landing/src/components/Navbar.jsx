import { useState, useEffect } from "react";
import { motion, AnimatePresence, useScroll, useSpring } from "framer-motion";
import { Sun, Moon, Github, Star } from "lucide-react";
import { useGithubStars, fmtStars } from "../hooks/useGithubStars";

export default function Navbar({ theme, toggleTheme }) {
  const stars = useGithubStars();
  const [scrolled, setScrolled] = useState(false);
  const { scrollYProgress } = useScroll();
  const progressScaleX = useSpring(scrollYProgress, {
    stiffness: 140,
    damping: 28,
    restDelta: 0.001,
  });

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

        <div className="flex items-center gap-1.5">
          {/* Get early access pill — appears when scrolled */}
          <AnimatePresence>
            {scrolled && (
              <motion.a
                key="early-access-pill"
                href="#waitlist"
                initial={{ opacity: 0, scale: 0.86, x: 12 }}
                animate={{ opacity: 1, scale: 1, x: 0 }}
                exit={{ opacity: 0, scale: 0.86, x: 12 }}
                transition={{ type: "spring", stiffness: 380, damping: 28 }}
                className="hidden sm:inline-flex button-sheen items-center gap-1.5 px-4 py-1.5 rounded-full text-xs font-semibold text-white no-underline"
                style={{
                  background: "linear-gradient(135deg, var(--grad-a), var(--grad-b))",
                  boxShadow: "0 3px 14px rgba(79,70,229,0.35)",
                }}
                whileHover={{ scale: 1.04, transition: { type: "spring", stiffness: 400, damping: 18 } }}
                whileTap={{ scale: 0.97 }}
              >
                Get early access
              </motion.a>
            )}
          </AnimatePresence>

          <motion.a
            href="https://github.com/francescogabrieli/Spectra"
            target="_blank"
            rel="noopener noreferrer"
            className="hidden sm:inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium no-underline"
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
            {fmtStars(stars) ? (
              <span
                className="flex items-center gap-0.5 px-1.5 py-0.5 rounded-md"
                style={{ backgroundColor: "var(--bg-tertiary)", color: "var(--text-tertiary)", fontSize: "10px", fontWeight: 600 }}
              >
                <Star size={8} style={{ opacity: 0.7 }} />
                {fmtStars(stars)}
              </span>
            ) : (
              <Star size={10} style={{ opacity: 0.5 }} />
            )}
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

      <motion.div
        className="absolute bottom-0 left-0 right-0 h-[2px] origin-left"
        style={{
          scaleX: progressScaleX,
          background: "linear-gradient(90deg, var(--grad-a), var(--grad-b))",
          opacity: scrolled ? 0.95 : 0.7,
        }}
      />
    </motion.nav>
  );
}
