/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { useEffect, useMemo, useRef, useState, type FormEvent } from 'react';
import { DEFAULT_PORTFOLIO } from './data/defaultPortfolio';
import type {
  ContactSubmitResponse,
  PortfolioPayload,
  SkillCategory,
  SkillItem,
} from './types/portfolio';

const SKILL_FILTERS: { id: SkillCategory; label: string }[] = [
  { id: 'all', label: 'All' },
  { id: 'languages', label: 'Languages' },
  { id: 'web', label: 'Web' },
  { id: 'tools', label: 'Dev Tools' },
];

export default function App() {
  const [portfolio, setPortfolio] = useState<PortfolioPayload>(DEFAULT_PORTFOLIO);
  const [theme, setTheme] = useState<'dark' | 'light'>(() => {
    try {
      const saved = localStorage.getItem('sai-portfolio-theme');
      return saved === 'light' ? 'light' : 'dark';
    } catch {
      return 'dark';
    }
  });
  const [menuOpen, setMenuOpen] = useState(false);
  const [typedRole, setTypedRole] = useState('');
  const [skillFilter, setSkillFilter] = useState<SkillCategory>('all');
  const [filteredSkills, setFilteredSkills] = useState<SkillItem[]>(DEFAULT_PORTFOLIO.skills.items);
  const [activeTopicId, setActiveTopicId] = useState<string>('oop');
  const [activeArchId, setActiveArchId] = useState<string>('overview');

  const [senderName, setSenderName] = useState('');
  const [senderEmail, setSenderEmail] = useState('');
  const [senderMessage, setSenderMessage] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const [toastMsg, setToastMsg] = useState('');
  const [toastVisible, setToastVisible] = useState(false);
  const toastTimerRef = useRef<number | null>(null);
  const [barsAnimated, setBarsAnimated] = useState(false);

  const showToast = (msg: string) => {
    setToastMsg(msg);
    setToastVisible(true);
    if (toastTimerRef.current !== null) {
      window.clearTimeout(toastTimerRef.current);
    }
    toastTimerRef.current = window.setTimeout(() => {
      setToastVisible(false);
    }, 2600);
  };

  // Sync theme attribute on documentElement
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    try {
      localStorage.setItem('sai-portfolio-theme', theme);
    } catch {
      // ignore storage errors
    }
  }, [theme]);

  // Hydrate portfolio data from Python backend (/api/portfolio)
  useEffect(() => {
    let active = true;
    fetch('/api/portfolio')
      .then((res) => (res.ok ? res.json() : null))
      .then((data: PortfolioPayload | null) => {
        if (!active || !data || !data.hero) return;
        setPortfolio(data);
        if (data.skills?.items) {
          setFilteredSkills(data.skills.items);
        }
      })
      .catch(() => {
        // Keep seamless default payload when offline
      });
    return () => {
      active = false;
    };
  }, []);

  // Role typing effect
  useEffect(() => {
    const roles = portfolio.hero.roles;
    if (!roles.length) return;

    let roleIdx = 0;
    let charIdx = 0;
    let deleting = false;
    let timerId = 0;

    const tick = () => {
      const current = roles[roleIdx] ?? roles[0];
      if (!deleting) {
        charIdx += 1;
        setTypedRole(current.slice(0, charIdx));
        if (charIdx >= current.length) {
          deleting = true;
          timerId = window.setTimeout(tick, 1700);
          return;
        }
      } else {
        charIdx = Math.max(0, charIdx - 1);
        setTypedRole(current.slice(0, charIdx));
        if (charIdx === 0) {
          deleting = false;
          roleIdx = (roleIdx + 1) % roles.length;
        }
      }
      timerId = window.setTimeout(tick, deleting ? 36 : 62);
    };

    timerId = window.setTimeout(tick, 120);
    return () => window.clearTimeout(timerId);
  }, [portfolio.hero.roles]);

  // Scroll reveal & progress bars observer
  useEffect(() => {
    const elements = Array.from(document.querySelectorAll<HTMLElement>('.reveal'));
    if (!('IntersectionObserver' in window)) {
      elements.forEach((el) => el.classList.add('visible'));
      setBarsAnimated(true);
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('visible');
            if (entry.target.closest('#education')) {
              setBarsAnimated(true);
            }
          }
        });
      },
      { threshold: 0.14 },
    );

    elements.forEach((el) => observer.observe(el));
    const fallbackTimer = window.setTimeout(() => setBarsAnimated(true), 600);

    return () => {
      observer.disconnect();
      window.clearTimeout(fallbackTimer);
    };
  }, []);

  const handleSkillFilter = async (category: SkillCategory) => {
    setSkillFilter(category);
    const localMatch =
      category === 'all'
        ? portfolio.skills.items
        : portfolio.skills.items.filter((item) => item.category === category);
    setFilteredSkills(localMatch);

    try {
      const res = await fetch(`/api/skills?category=${encodeURIComponent(category)}`);
      if (res.ok) {
        const data = await res.json();
        if (Array.isArray(data?.items)) {
          setFilteredSkills(data.items);
        }
      }
    } catch {
      // Local fallback already applied
    }
  };

  const handleCopy = async (value: string) => {
    try {
      await navigator.clipboard.writeText(value);
      showToast(`Copied: ${value}`);
    } catch {
      showToast(`Copy manually: ${value}`);
    }
  };

  const handleContactSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const name = senderName.trim();
    const email = senderEmail.trim();
    const message = senderMessage.trim();
    if (!name || !email || !message || submitting) return;

    setSubmitting(true);
    try {
      const res = await fetch('/api/contact', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, email, message }),
      });
      const result: ContactSubmitResponse = await res.json();
      if (!res.ok || !result.ok) {
        showToast(result.message || 'Please check your message details.');
        return;
      }
      showToast(result.confirmation || 'Opening your email client...');
      if (result.mailto_url) {
        window.location.href = result.mailto_url;
      }
      setSenderName('');
      setSenderEmail('');
      setSenderMessage('');
    } catch {
      const subject = encodeURIComponent(`Portfolio Inquiry from ${name}`);
      const body = encodeURIComponent(`Name: ${name}\nEmail: ${email}\n\n${message}`);
      window.location.href = `mailto:chakravarthi000087@gmail.com?subject=${subject}&body=${body}`;
      showToast('Opening your email client...');
    } finally {
      setSubmitting(false);
    }
  };

  const activeTopic = useMemo(
    () =>
      portfolio.core_knowledge.find((t) => t.id === activeTopicId) ??
      portfolio.core_knowledge[0],
    [portfolio.core_knowledge, activeTopicId],
  );

  const activeLayer = useMemo(
    () =>
      portfolio.featured_project.layers.find((l) => l.id === activeArchId) ??
      portfolio.featured_project.layers[0],
    [portfolio.featured_project.layers, activeArchId],
  );

  const currentYear = new Date().getFullYear();

  return (
    <>
      <div className="bg-grid" aria-hidden="true" />
      <div className="bg-orb bg-orb-1" aria-hidden="true" />
      <div className="bg-orb bg-orb-2" aria-hidden="true" />

      {/* Navbar */}
      <header className="navbar">
        <div className="container nav-inner">
          <a href="#top" className="brand">
            <span className="brand-badge">{portfolio.hero.brand_initials}</span>
            <span>{portfolio.hero.brand_name}</span>
          </a>

          <ul className={`nav-links ${menuOpen ? 'open' : ''}`} id="navLinks">
            {['education', 'skills', 'projects', 'achievements', 'contact'].map((section) => (
              <li key={section}>
                <a href={`#${section}`} onClick={() => setMenuOpen(false)}>
                  {section.charAt(0).toUpperCase() + section.slice(1)}
                </a>
              </li>
            ))}
          </ul>

          <div className="nav-actions">
            <button
              type="button"
              className="icon-btn"
              id="themeToggle"
              aria-label="Toggle dark or light theme"
              title="Toggle theme"
              onClick={() => setTheme((prev) => (prev === 'dark' ? 'light' : 'dark'))}
            >
              <span>{theme === 'light' ? '🌙' : '☀️'}</span>
            </button>
            <button
              type="button"
              className="icon-btn menu-toggle"
              id="menuToggle"
              aria-label="Toggle navigation menu"
              onClick={() => setMenuOpen((prev) => !prev)}
            >
              ☰
            </button>
          </div>
        </div>
      </header>

      <main id="top">
        {/* Hero */}
        <section className="hero">
          <div className="container hero-grid">
            <div>
              <div className="status-pill">
                <span className="status-dot" />
                <span>{portfolio.hero.status_badge}</span>
              </div>

              <h1>
                Hi, I&apos;m <span className="gradient-text">{portfolio.hero.full_name}</span>
              </h1>

              <div className="role-line" aria-live="polite">
                <span>{typedRole}</span>
                <span className="cursor" />
              </div>

              <p className="hero-summary">{portfolio.hero.summary}</p>

              <div className="hero-ctas">
                <a href="#projects" className="btn btn-primary">
                  Explore Project Architecture
                </a>
                <a href="#contact" className="btn btn-secondary">
                  Get in Touch
                </a>
                <a
                  href={portfolio.hero.github_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn btn-secondary"
                >
                  GitHub ↗
                </a>
              </div>

              <div className="hero-meta">
                <span>📍 {portfolio.hero.location}</span>
                <span>🎓 {portfolio.hero.university_short}</span>
                <span>🏆 {portfolio.hero.hackathon_badge}</span>
              </div>
            </div>

            {/* Portrait */}
            <div className="portrait-wrap">
              <div className="portrait-card">
                <div className="portrait-frame">
                  {portfolio.has_profile_photo && portfolio.profile_photo_url ? (
                    <img
                      src={portfolio.profile_photo_url}
                      alt={`Portrait of ${portfolio.hero.full_name}`}
                      referrerPolicy="no-referrer"
                    />
                  ) : (
                    <div className="portrait-fallback">
                      <div className="fallback-initials">{portfolio.hero.initials_fallback}</div>
                      <strong>{portfolio.hero.full_name}</strong>
                      <small style={{ color: '#94a3b8', marginTop: '6px' }}>
                        Place your photo as <code>public/profile.jpg</code> to display it here.
                      </small>
                    </div>
                  )}
                </div>

                <div className="float-chip">
                  <span>⚡</span>
                  <div>
                    <strong>{portfolio.hero.float_chip_title}</strong>
                    <span style={{ color: 'var(--text-muted)' }}>
                      {portfolio.hero.float_chip_subtitle}
                    </span>
                  </div>
                </div>

                <div className="portrait-caption">
                  <div>
                    <strong>{portfolio.hero.full_name}</strong>
                    <span>{portfolio.hero.batch_period}</span>
                  </div>
                  <a
                    href={portfolio.hero.linkedin_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="copy-btn"
                  >
                    LinkedIn ↗
                  </a>
                </div>
              </div>
            </div>
          </div>

          {/* Quick Stats */}
          <div className="container stats-grid reveal">
            {portfolio.hero.quick_stats.map((stat) => (
              <div className="stat-box" key={stat.label}>
                <div className="stat-num">{stat.value}</div>
                <div className="stat-label">{stat.label}</div>
              </div>
            ))}
          </div>
        </section>

        {/* Education */}
        <section id="education">
          <div className="container">
            <div className="section-header reveal">
              <div>
                <span className="section-tag">Academic Foundation</span>
                <h2 className="section-title">Education &amp; Performance</h2>
              </div>
              <p className="section-sub">
                Building strong computer science fundamentals alongside hands-on development practice.
              </p>
            </div>

            <div className="edu-grid reveal">
              <div className="card">
                <span className="edu-badge">{portfolio.education.period}</span>
                <h3 style={{ fontSize: '1.15rem', fontWeight: 700 }}>
                  {portfolio.education.institution}
                </h3>
                <p style={{ color: 'var(--text-soft)', marginTop: '4px', fontWeight: 500 }}>
                  {portfolio.education.degree}
                </p>
                <div className="edu-meta">
                  <span>📘 {portfolio.education.current_year_label}</span>
                  <span>💻 {portfolio.education.focus}</span>
                </div>

                <div style={{ marginTop: '22px' }}>
                  <div
                    style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      fontSize: '0.86rem',
                      color: 'var(--text-muted)',
                    }}
                  >
                    <span>
                      Degree Progress (Semester {portfolio.education.current_semester} of{' '}
                      {portfolio.education.total_semesters})
                    </span>
                    <strong style={{ color: 'var(--text)', fontFamily: 'var(--font-mono)' }}>
                      {portfolio.education.degree_progress_percent}%
                    </strong>
                  </div>
                  <div className="progress-track">
                    <div
                      className="progress-fill"
                      style={{
                        width: barsAnimated
                          ? `${portfolio.education.degree_progress_percent}%`
                          : '0%',
                      }}
                    />
                  </div>
                </div>
              </div>

              <div className="card">
                <h3 style={{ fontSize: '1.15rem', fontWeight: 700 }}>Semester SGPA Breakdown</h3>
                <p style={{ fontSize: '0.88rem', color: 'var(--text-muted)' }}>
                  Consistent academic performance across core engineering semesters.
                </p>

                <div className="sgpa-bars">
                  {portfolio.education.semesters.map((sem) => (
                    <div key={sem.semester}>
                      <div className="sgpa-row-top">
                        <span>{sem.label}</span>
                        <strong
                          style={
                            sem.sgpa === null ? { color: 'var(--accent-2)' } : undefined
                          }
                        >
                          {sem.display_score}
                        </strong>
                      </div>
                      <div className="progress-track" style={{ marginTop: 0 }}>
                        <div
                          className="progress-fill"
                          style={{
                            width: barsAnimated ? `${sem.progress_percent}%` : '0%',
                          }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Skills */}
        <section id="skills">
          <div className="container">
            <div className="section-header reveal">
              <div>
                <span className="section-tag">Technical Stack</span>
                <h2 className="section-title">Skills &amp; Core Knowledge</h2>
              </div>

              <div className="filter-bar" role="tablist" aria-label="Filter skills by category">
                {SKILL_FILTERS.map((filter) => (
                  <button
                    key={filter.id}
                    type="button"
                    className={`filter-btn ${skillFilter === filter.id ? 'active' : ''}`}
                    onClick={() => handleSkillFilter(filter.id)}
                  >
                    {filter.label}
                  </button>
                ))}
              </div>
            </div>

            <div className="skills-grid reveal" id="skillsGrid">
              {filteredSkills.map((skill) => (
                <div className="skill-card" key={skill.id}>
                  <div className="skill-top">
                    <span className="skill-name">{skill.name}</span>
                    <span
                      className={`level-pill ${
                        skill.level === 'Intermediate' ? 'level-intermediate' : 'level-beginner'
                      }`}
                    >
                      {skill.level}
                    </span>
                  </div>
                  <div className="skill-cat">{skill.category_label}</div>
                  <div className="mini-bar">
                    <span style={{ width: `${skill.proficiency}%` }} />
                  </div>
                </div>
              ))}
            </div>

            {/* Core CS Knowledge Interactive Explorer */}
            <div className="card core-box reveal">
              <div>
                <h3 style={{ marginBottom: '8px', fontSize: '1.15rem', fontWeight: 700 }}>
                  Core Computer Science Knowledge
                </h3>
                <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)', marginBottom: '14px' }}>
                  Click any subject to explore how it supports my software &amp; web engineering
                  journey.
                </p>
                <div className="pill-group" id="corePills">
                  {portfolio.core_knowledge.map((topic) => (
                    <button
                      key={topic.id}
                      type="button"
                      className={`topic-pill ${activeTopic?.id === topic.id ? 'active' : ''}`}
                      onClick={() => setActiveTopicId(topic.id)}
                    >
                      {topic.short_label}
                    </button>
                  ))}
                </div>
              </div>

              {activeTopic && (
                <div className="topic-detail" id="topicDetail">
                  <h4>{activeTopic.title}</h4>
                  <p>{activeTopic.description}</p>
                </div>
              )}
            </div>
          </div>
        </section>

        {/* Projects */}
        <section id="projects">
          <div className="container">
            <div className="section-header reveal">
              <div>
                <span className="section-tag">Featured Project</span>
                <h2 className="section-title">Projects &amp; System Design</h2>
              </div>
              <p className="section-sub">
                Interactive breakdown of the planned architecture and foundation for Trip Guide.
              </p>
            </div>

            <div className="card project-card reveal">
              <div>
                <span className="stage-badge">🛠️ {portfolio.featured_project.stage_label}</span>
                <h3 style={{ fontSize: '1.5rem', marginBottom: '10px', fontWeight: 700 }}>
                  {portfolio.featured_project.title}
                </h3>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.97rem' }}>
                  {portfolio.featured_project.description}
                </p>

                <div className="tech-tags">
                  {portfolio.featured_project.tech_tags.map((tag) => (
                    <span className="tech-tag" key={tag}>
                      {tag}
                    </span>
                  ))}
                </div>

                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '12px' }}>
                  <a
                    href={portfolio.featured_project.live_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn btn-primary"
                  >
                    Visit Project Website ↗
                  </a>
                  <a
                    href={portfolio.featured_project.github_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn btn-secondary"
                  >
                    GitHub Profile
                  </a>
                </div>
              </div>

              {/* Interactive Architecture Explorer */}
              <div className="arch-explorer">
                <div
                  style={{
                    fontSize: '0.8rem',
                    fontFamily: 'var(--font-mono)',
                    color: 'var(--text-muted)',
                    marginBottom: '10px',
                  }}
                >
                  INTERACTIVE ARCHITECTURE EXPLORER
                </div>
                <div className="arch-tabs" role="tablist">
                  {portfolio.featured_project.layers.map((layer) => (
                    <button
                      key={layer.id}
                      type="button"
                      className={`arch-tab ${activeLayer?.id === layer.id ? 'active' : ''}`}
                      onClick={() => setActiveArchId(layer.id)}
                    >
                      {layer.tab_label}
                    </button>
                  ))}
                </div>

                {activeLayer && (
                  <div className="arch-panel" key={activeLayer.id}>
                    <h4>{activeLayer.title}</h4>
                    <p>{activeLayer.summary}</p>
                    <ul className="arch-list">
                      {activeLayer.highlights.map((item) => (
                        <li key={item}>{item}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          </div>
        </section>

        {/* Achievements & Info */}
        <section id="achievements">
          <div className="container">
            <div className="section-header reveal">
              <div>
                <span className="section-tag">Beyond Academics</span>
                <h2 className="section-title">Achievements &amp; Profile</h2>
              </div>
            </div>

            <div className="info-grid reveal">
              {portfolio.achievements.map((card) => (
                <div className="card info-card" key={card.id}>
                  <h3>
                    {card.icon} {card.title}
                  </h3>
                  <p style={{ color: 'var(--text-muted)', fontSize: '0.93rem' }}>
                    {card.description}
                  </p>
                  <div className="chip-row">
                    {card.chips.map((chip, idx) => (
                      <span
                        className="chip"
                        key={chip}
                        style={
                          card.highlight_first_chip && idx === 0
                            ? { borderColor: 'rgba(245,158,11,0.4)', color: 'var(--accent-2)' }
                            : undefined
                        }
                      >
                        {chip}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Contact */}
        <section id="contact">
          <div className="container">
            <div className="section-header reveal">
              <div>
                <span className="section-tag">Connect</span>
                <h2 className="section-title">Get in Touch</h2>
              </div>
              <p className="section-sub">
                Open to internships, student collaborations, hackathons, and learning opportunities.
              </p>
            </div>

            <div className="contact-grid reveal">
              <div className="card">
                {portfolio.contact_channels.map((channel, index) => (
                  <div
                    className="contact-item"
                    key={channel.id}
                    style={
                      index === portfolio.contact_channels.length - 1
                        ? { marginBottom: 0 }
                        : undefined
                    }
                  >
                    <div>
                      <small>{channel.label}</small>
                      <strong>{channel.display_value}</strong>
                    </div>
                    {channel.action_type === 'copy' ? (
                      <button
                        type="button"
                        className="copy-btn"
                        onClick={() => handleCopy(channel.action_value)}
                      >
                        Copy
                      </button>
                    ) : (
                      <a
                        className="copy-btn"
                        href={channel.action_value}
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        Open ↗
                      </a>
                    )}
                  </div>
                ))}
              </div>

              <form className="card" id="contactForm" onSubmit={handleContactSubmit}>
                <h3 style={{ marginBottom: '14px', fontSize: '1.15rem', fontWeight: 700 }}>
                  Send a Quick Message
                </h3>
                <div className="form-group">
                  <label htmlFor="senderName">Your Name</label>
                  <input
                    id="senderName"
                    type="text"
                    placeholder="Enter your name"
                    value={senderName}
                    onChange={(e) => setSenderName(e.target.value)}
                    required
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="senderEmail">Your Email</label>
                  <input
                    id="senderEmail"
                    type="email"
                    placeholder="you@example.com"
                    value={senderEmail}
                    onChange={(e) => setSenderEmail(e.target.value)}
                    required
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="senderMessage">Message</label>
                  <textarea
                    id="senderMessage"
                    rows={4}
                    placeholder="Hi Sai, I'd love to connect about..."
                    value={senderMessage}
                    onChange={(e) => setSenderMessage(e.target.value)}
                    required
                  />
                </div>
                <button
                  type="submit"
                  className="btn btn-primary"
                  style={{ width: '100%' }}
                  disabled={submitting}
                >
                  {submitting ? 'Preparing Message...' : 'Compose Email to Sai'}
                </button>
              </form>
            </div>
          </div>
        </section>
      </main>

      <footer>
        <div className="container footer-inner">
          <span>
            © {currentYear} {portfolio.hero.full_name} • {portfolio.hero.location}
          </span>
          <span>Powered by Python Backend &amp; React</span>
        </div>
      </footer>

      <div className={`toast ${toastVisible ? 'show' : ''}`} id="toast" role="status" aria-live="polite">
        {toastMsg}
      </div>
    </>
  );
}
