import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ArrowRight, X } from "lucide-react";

export default function StickyMobileCTA() {
  const [visible, setVisible] = useState(false);
  const [dismissed, setDismissed] = useState(false);

  useEffect(() => {
    // Don't show if user already joined
    if (localStorage.getItem("spectra-waitlist-joined")) {
      setDismissed(true);
      return;
    }
    const onScroll = () => {
      setVisible(window.scrollY > window.innerHeight * 0.65);
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <AnimatePresence>
      {visible && !dismissed && (
        <motion.div
          key="sticky-cta"
          initial={{ y: 120, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: 120, opacity: 0 }}
          transition={{ type: "spring", stiffness: 340, damping: 28 }}
          className="fixed bottom-0 left-0 right-0 z-40 sm:hidden px-4 pb-5 pt-2 pointer-events-none"
        >
          <div className="flex gap-2 max-w-sm mx-auto pointer-events-auto">
            <motion.a
              href="#waitlist"
              className="button-sheen flex-1 flex items-center justify-center gap-2 py-3.5 rounded-2xl text-sm font-semibold text-white no-underline"
              style={{
                background: "linear-gradient(135deg, var(--grad-a), var(--grad-b))",
                boxShadow: "0 6px 28px rgba(79,70,229,0.45), inset 0 1px 0 rgba(255,255,255,0.12)",
              }}
              whileTap={{ scale: 0.97 }}
              onClick={() => setDismissed(true)}
            >
              Join waitlist — it&apos;s free
              <ArrowRight size={15} />
            </motion.a>
            <motion.button
              onClick={() => setDismissed(true)}
              aria-label="Dismiss"
              className="w-[52px] rounded-2xl flex items-center justify-center cursor-pointer"
              style={{
                backgroundColor: "var(--bg-tertiary)",
                border: "1px solid var(--border)",
                color: "var(--text-tertiary)",
              }}
              whileTap={{ scale: 0.95 }}
            >
              <X size={16} />
            </motion.button>
          </div>
          {/* Safe area gradient so bar doesn't clash with home indicator */}
          <div
            className="absolute inset-x-0 bottom-0 h-5 pointer-events-none"
            style={{ background: "var(--bg)" }}
          />
        </motion.div>
      )}
    </AnimatePresence>
  );
}
