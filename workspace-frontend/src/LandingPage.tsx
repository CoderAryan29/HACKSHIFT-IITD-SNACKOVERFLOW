import { useState } from "react";
import { ArrowDown, ArrowRight, Leaf, Menu, X } from "lucide-react";
import type { Page } from "./data";
import heroImage from "./assets/kisansetu-hero.png";
import "./landing-page.css";

interface LandingPageProps {
  onNavigate: (page: Page) => void;
  onOpenAccount: () => void;
}

const links: { label: string; page: Page }[] = [
  { label: "Home", page: "Home" },
  { label: "Marketplace", page: "Marketplace" },
  { label: "Government Schemes", page: "Schemes" },
  { label: "Crop Health", page: "Crop Health" },
  { label: "Farm Ledger", page: "My Farm" },
  { label: "AI Assistant", page: "Ask KisanSetu" },
  { label: "Legal Aid", page: "Legal Aid" },
];

export default function LandingPage({ onNavigate, onOpenAccount }: LandingPageProps) {
  const [menuOpen, setMenuOpen] = useState(false);

  function navigate(page: Page) {
    setMenuOpen(false);
    onNavigate(page);
  }

  return (
    <main
      className="landing-page"
      style={{ backgroundImage: `linear-gradient(180deg, rgba(6, 24, 29, .54) 0%, rgba(8, 23, 23, .18) 34%, rgba(10, 25, 18, .36) 100%), linear-gradient(90deg, rgba(8, 22, 18, .12), rgba(7, 22, 20, .18)), url("${heroImage}")` }}
    >
      <header className="landing-header">
        <button className="landing-brand" onClick={() => navigate("Home")} aria-label="KisanSetu home">
          <span className="landing-brand-icon"><Leaf size={31} strokeWidth={2.2} /></span>
          <span className="landing-brand-copy">
            <strong>KisanSetu</strong>
            <span>Saath Har Kisan Ka</span>
          </span>
        </button>

        <button
          className="landing-menu-toggle"
          aria-label={menuOpen ? "Close navigation menu" : "Open navigation menu"}
          aria-expanded={menuOpen}
          aria-controls="landing-navigation"
          onClick={() => setMenuOpen(open => !open)}
        >
          {menuOpen ? <X size={23} /> : <Menu size={23} />}
        </button>

        <nav
          id="landing-navigation"
          className={`landing-navigation${menuOpen ? " is-open" : ""}`}
          aria-label="Main navigation"
        >
          {links.map((link, index) => (
            <button
              key={link.page}
              className={`landing-nav-link${index === 0 ? " is-current" : ""}`}
              aria-current={index === 0 ? "page" : undefined}
              onClick={() => navigate(link.page)}
            >
              {link.label}
            </button>
          ))}
          <button
            className="landing-account landing-account-mobile"
            onClick={() => {
              setMenuOpen(false);
              onOpenAccount();
            }}
          >
            Login / Sign Up
          </button>
        </nav>

        <button className="landing-account landing-account-desktop" onClick={onOpenAccount}>
          Login / Sign Up
        </button>
      </header>

      <section className="landing-hero-content" aria-labelledby="landing-title">
        <h1 id="landing-title">
          <span className="landing-title-first">A Stronger Tomorrow</span>
          <span>for <em>Every Farmer</em></span>
        </h1>
        <p>
          Better prices. Smarter decisions. Healthier crops.
          <span>All in one platform.</span>
        </p>
        <button className="landing-cta" onClick={() => navigate("Home")}>
          Get Started <ArrowRight size={19} strokeWidth={2.3} />
        </button>
      </section>

      <button className="landing-scroll" onClick={() => navigate("Home")} aria-label="Scroll to explore the KisanSetu dashboard">
        <span className="landing-mouse" aria-hidden="true"><span /></span>
        <span>Scroll to explore</span>
        <ArrowDown size={17} strokeWidth={1.8} aria-hidden="true" />
      </button>
    </main>
  );
}
