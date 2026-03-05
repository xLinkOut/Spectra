import { useEffect, useRef, useState } from "react";
import { AnimatePresence, motion, useMotionValue, useSpring, useTransform, useReducedMotion } from "framer-motion";
import { ArrowRight, Github, ChevronLeft, ChevronRight, Star } from "lucide-react";
import { staggerContainer, fadeUp, ease } from "../lib/motion";
import { useGithubStars, fmtStars } from "../hooks/useGithubStars";

const HEADLINE = ["Know where", "your money", "actually goes."];

const stats = [
  { value: "CSV & PDF", label: "any bank, any format" },
  { value: "100% offline", label: "nothing leaves your device" },
  { value: "6-layer AI", label: "categorization cascade" },
];

const LOCAL_SHOTS = [
  { src: "/local-1.png", title: "Dashboard", subtitle: "Overview + insights" },
  { src: "/local-2.png", title: "Transactions", subtitle: "Movimenti locali" },
  { src: "/local-3.png", title: "Trends", subtitle: "Trend & recurring" },
  { src: "/local-4.png", title: "Settings", subtitle: "Config + rules" },
];

const shotVariants = {
  enter: (direction) => ({ opacity: 0, x: direction > 0 ? 72 : -72, scale: 0.98, filter: "blur(7px)" }),
  center: {
    opacity: 1,
    x: 0,
    scale: 1,
    filter: "blur(0px)",
    transition: { duration: 0.7, ease: [0.16, 1, 0.3, 1] },
  },
  exit: (direction) => ({
    opacity: 0,
    x: direction > 0 ? -72 : 72,
    scale: 1.01,
    filter: "blur(6px)",
    transition: { duration: 0.45, ease: [0.4, 0, 1, 1] },
  }),
};

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
  const [activeShot, setActiveShot] = useState(0);
  const [direction, setDirection] = useState(1);
  const [isPaused, setIsPaused] = useState(false);
  const shouldReduceMotion = useReducedMotion();
  const stars = useGithubStars();
  const mouseX = useMotionValue(typeof window !== "undefined" ? window.innerWidth / 2 : 400);
  const mouseY = useMotionValue(300);
  const springX = useSpring(mouseX, { stiffness: 60, damping: 20 });
  const springY = useSpring(mouseY, { stiffness: 60, damping: 20 });
  const rotateX = useTransform(springY, [0, 900], [4.8, -4.8]);
  const rotateY = useTransform(springX, [0, 1300], [-5.8, 5.8]);
  const sheenOffset = useTransform(springX, [0, 1300], [-16, 16]);

  useEffect(() => {
    if (isPaused) return;
    const timer = setInterval(() => {
      setDirection(1);
      setActiveShot((prev) => (prev + 1) % LOCAL_SHOTS.length);
    }, 3200);
    return () => clearInterval(timer);
  }, [isPaused]);

  const paginateShots = (nextDirection) => {
    setDirection(nextDirection);
    setActiveShot((prev) => (prev + nextDirection + LOCAL_SHOTS.length) % LOCAL_SHOTS.length);
  };

  const goToShot = (index) => {
    if (index === activeShot) return;
    setDirection(index > activeShot ? 1 : -1);
    setActiveShot(index);
  };

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
          className="text-6xl sm:text-7xl md:text-[5.25rem] font-bold tracking-[-0.035em] leading-[1.14] mb-7"
          style={{ color: "var(--text-primary)" }}
        >
          {HEADLINE.map((line, li) => (
            <span key={li} className="block pb-[0.08em] last:pb-0">
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
            className="group button-sheen inline-flex items-center gap-2 px-7 py-3.5 rounded-xl text-sm font-semibold text-white no-underline"
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
            {fmtStars(stars) && (
              <span
                className="flex items-center gap-1 px-1.5 py-0.5 rounded-md"
                style={{
                  backgroundColor: "var(--bg-secondary)",
                  color: "var(--text-tertiary)",
                  fontSize: "11px",
                  fontWeight: 600,
                  border: "1px solid var(--border)",
                }}
              >
                <Star size={9} style={{ opacity: 0.8 }} />
                {fmtStars(stars)}
              </span>
            )}
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
        <motion.div
          className="relative"
          style={
            shouldReduceMotion
              ? undefined
              : {
                  rotateX,
                  rotateY,
                  transformPerspective: 1700,
                  transformStyle: "preserve-3d",
                }
          }
          transition={{ type: "spring", stiffness: 80, damping: 22 }}
        >
          <BrowserMockup>
            {/* Fixed-ratio container: images are ~1400×713 (≈ 2:1) — this prevents height jumps between slides */}
            <div
              className="relative overflow-hidden carousel-scan"
              style={{ aspectRatio: "1400 / 713" }}
              onMouseEnter={() => setIsPaused(true)}
              onMouseLeave={() => setIsPaused(false)}
            >
              <AnimatePresence initial={false} custom={direction} mode="wait">
                <motion.img
                  key={LOCAL_SHOTS[activeShot].src}
                  src={LOCAL_SHOTS[activeShot].src}
                  alt={`Spectra Local UI — ${LOCAL_SHOTS[activeShot].title}`}
                  custom={direction}
                  variants={shotVariants}
                  initial="enter"
                  animate="center"
                  exit="exit"
                  className="absolute inset-0 w-full h-full select-none"
                  style={{ objectFit: "cover", objectPosition: "top center" }}
                  drag="x"
                  dragConstraints={{ left: 0, right: 0 }}
                  dragElastic={0.12}
                  onDragEnd={(_, info) => {
                    if (info.offset.x < -70 || info.velocity.x < -320) paginateShots(1);
                    if (info.offset.x > 70 || info.velocity.x > 320) paginateShots(-1);
                  }}
                  loading="lazy"
                />
              </AnimatePresence>

              <motion.div
                className="absolute inset-y-0 -left-[24%] w-[46%] pointer-events-none"
                style={{
                  x: shouldReduceMotion ? 0 : sheenOffset,
                  background: "linear-gradient(100deg, transparent 0%, rgba(255,255,255,0.18) 48%, transparent 100%)",
                  filter: "blur(2px)",
                }}
              />

              <div
                className="absolute top-4 left-4 px-3 py-1.5 rounded-lg backdrop-blur-md"
                style={{
                  background: "rgba(9, 9, 11, 0.55)",
                  border: "1px solid rgba(255,255,255,0.16)",
                  color: "#f4f4f5",
                }}
              >
                <div className="text-[12px] font-semibold tracking-tight">{LOCAL_SHOTS[activeShot].title}</div>
                <div className="text-[11px]" style={{ opacity: 0.72 }}>
                  {LOCAL_SHOTS[activeShot].subtitle}
                </div>
              </div>

              <div className="absolute inset-y-0 left-0 flex items-center pl-3">
                <motion.button
                  aria-label="Previous screenshot"
                  onClick={() => paginateShots(-1)}
                  className="w-9 h-9 rounded-full flex items-center justify-center"
                  style={{
                    background: "rgba(9,9,11,0.5)",
                    border: "1px solid rgba(255,255,255,0.18)",
                    color: "#fafafa",
                  }}
                  whileHover={{ scale: 1.06, backgroundColor: "rgba(9,9,11,0.7)" }}
                  whileTap={{ scale: 0.94 }}
                >
                  <ChevronLeft size={16} />
                </motion.button>
              </div>

              <div className="absolute inset-y-0 right-0 flex items-center pr-3">
                <motion.button
                  aria-label="Next screenshot"
                  onClick={() => paginateShots(1)}
                  className="w-9 h-9 rounded-full flex items-center justify-center"
                  style={{
                    background: "rgba(9,9,11,0.5)",
                    border: "1px solid rgba(255,255,255,0.18)",
                    color: "#fafafa",
                  }}
                  whileHover={{ scale: 1.06, backgroundColor: "rgba(9,9,11,0.7)" }}
                  whileTap={{ scale: 0.94 }}
                >
                  <ChevronRight size={16} />
                </motion.button>
              </div>

              <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex items-center gap-2 px-2 py-1.5 rounded-full"
                style={{ background: "rgba(9,9,11,0.48)", border: "1px solid rgba(255,255,255,0.15)" }}
              >
                {LOCAL_SHOTS.map((_, index) => (
                  <button
                    key={index}
                    onClick={() => goToShot(index)}
                    className="h-1.5 rounded-full transition-all duration-300"
                    style={{
                      width: index === activeShot ? 20 : 6,
                      backgroundColor: index === activeShot ? "#a78bfa" : "rgba(255,255,255,0.45)",
                    }}
                    aria-label={`Go to screenshot ${index + 1}`}
                  />
                ))}
              </div>
            </div>
          </BrowserMockup>
          <motion.div
            className="pointer-events-none absolute -inset-3 rounded-[1.3rem]"
            style={{
              background: "radial-gradient(ellipse at top, rgba(124,58,237,0.2), transparent 65%)",
              filter: "blur(26px)",
              opacity: 0.7,
              zIndex: -1,
            }}
          />
        </motion.div>
        <div
          className="absolute bottom-0 left-0 right-0 h-48 pointer-events-none"
          style={{ background: "linear-gradient(to bottom, transparent, var(--bg))" }}
        />
      </motion.div>
    </section>
  );
}
