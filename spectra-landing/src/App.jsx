import "./App.css";
import { useTheme } from "./hooks/useTheme";
import Navbar from "./components/Navbar";
import Hero from "./components/Hero";
import HowItWorks from "./components/HowItWorks";
import Features from "./components/Features";
import Waitlist from "./components/Waitlist";
import GithubCTA from "./components/GithubCTA";
import Footer from "./components/Footer";
import StickyMobileCTA from "./components/StickyMobileCTA";

function App() {
  const { theme, toggle } = useTheme();

  return (
    <div className="min-h-screen relative overflow-x-clip" style={{ backgroundColor: "var(--bg)" }}>
      <div className="site-aurora" aria-hidden="true" />
      <div className="site-aurora site-aurora-alt" aria-hidden="true" />
      <div className="site-vignette" aria-hidden="true" />
      <Navbar theme={theme} toggleTheme={toggle} />
      <main className="relative z-10">
        <Hero />
        <HowItWorks />
        <Features />
        <Waitlist />
        <GithubCTA />
      </main>
      <div className="relative z-10">
        <Footer />
      </div>
      <StickyMobileCTA />
    </div>
  );
}

export default App;
