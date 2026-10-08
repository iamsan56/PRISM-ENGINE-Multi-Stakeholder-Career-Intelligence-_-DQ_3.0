import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Menu, X, ArrowUp, ChevronRight, BrainCircuit, Database, Code, Users } from 'lucide-react';
import { Canvas } from '@react-three/fiber';
import { ContactShadows, Environment, OrbitControls, Stars } from '@react-three/drei';
import heroImage from '../assets/hero.png';
import prismBg from '../assets/prism-bg.jpg';
import PrismMesh from '../components/PrismMesh';

const LandingPage = () => {
  const navigate = useNavigate();
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [showBackToTop, setShowBackToTop] = useState(false);

  // Scroll listener for "Back to Top" button
  useEffect(() => {
    const handleScroll = () => {
      if (window.scrollY > 300) setShowBackToTop(true);
      else setShowBackToTop(false);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const scrollToTop = () => window.scrollTo({ top: 0, behavior: 'smooth' });

  return (
    <div className="font-sans bg-white text-gray-900 relative">
      {/* 
        ========================================================================
        NAVIGATION (Hamburger Only)
        ========================================================================
      */}
      <nav className="fixed top-0 w-full z-50 p-6 flex justify-between items-center mix-blend-difference text-white">
        <div className="font-mono font-bold text-xl tracking-tighter">PRISM.</div>
        <button onClick={() => setIsMenuOpen(!isMenuOpen)} className="p-2 z-50 focus:outline-none">
          {isMenuOpen ? <X size={28} /> : <Menu size={28} />}
        </button>
      </nav>

      {/* Hidden Nav Overlay */}
      <div className={`fixed inset-0 bg-blue-600 z-40 transition-transform duration-500 flex flex-col justify-center items-center ${isMenuOpen ? 'translate-x-0' : 'translate-x-full'}`}>
        <ul className="text-white text-4xl space-y-8 font-light text-center">
          <li><a href="#hero" onClick={() => setIsMenuOpen(false)} className="hover:text-blue-200 transition-colors">Home</a></li>
          <li><a href="#problem" onClick={() => setIsMenuOpen(false)} className="hover:text-blue-200 transition-colors">The Divide</a></li>
          <li><a href="#architecture" onClick={() => setIsMenuOpen(false)} className="hover:text-blue-200 transition-colors">Engine</a></li>
          <li><a href="#team" onClick={() => setIsMenuOpen(false)} className="hover:text-blue-200 transition-colors">Four Spades</a></li>
        </ul>
      </div>

      {/* 
        ========================================================================
        HERO SECTION
        ========================================================================
      */}
      <section
        id="hero"
        className="min-h-[92vh] flex items-center px-4 pt-24 pb-16 relative overflow-hidden bg-slate-950 bg-cover bg-center bg-blend-overlay text-white"
        style={{ backgroundImage: `linear-gradient(rgba(2,6,23,.78), rgba(2,6,23,.88)), url(${prismBg})` }}
      >
        <div className="absolute inset-0 opacity-40 bg-[linear-gradient(90deg,rgba(34,211,238,.18)_1px,transparent_1px),linear-gradient(rgba(34,211,238,.12)_1px,transparent_1px)] bg-[size:42px_42px]"></div>
        <div className="relative mx-auto grid max-w-7xl items-center gap-12 lg:grid-cols-[1.05fr_.95fr]">
          <div className="text-left">
            <div className="mb-5 inline-flex rounded-full border border-cyan-300/30 bg-cyan-300/10 px-4 py-2 text-xs font-bold uppercase tracking-[0.24em] text-cyan-200">
              DataQuest 3.0 Career Intelligence
            </div>
            <h1 className="text-5xl md:text-7xl font-black tracking-tight leading-none">
              PRISM Engine
            </h1>
            <p className="mt-6 max-w-2xl text-lg md:text-xl leading-8 text-slate-300">
              A decision console that maps student psychometrics, parent finances, scholarships, ROI, and family alignment into ranked STEAM pathways.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <button 
                onClick={() => navigate('/assessment')}
                className="px-7 py-4 bg-cyan-400 hover:bg-cyan-300 text-slate-950 font-black rounded-xl flex items-center gap-3 transition-colors shadow-xl shadow-cyan-950/40"
              >
                RUN ASSESSMENT <ChevronRight size={20} />
              </button>
              <a href="#architecture" className="px-7 py-4 border border-white/20 bg-white/10 hover:bg-white/15 text-white font-bold rounded-xl transition-colors">
                VIEW ENGINE
              </a>
            </div>
            <div className="mt-10 grid grid-cols-3 gap-3 max-w-xl">
              {[
                ['45 ms', 'math pipeline'],
                ['PSCI', 'family conflict'],
                ['ROI', 'cost/value solver']
              ].map(([metric, label]) => (
                <div key={metric} className="border border-white/10 bg-white/[0.06] p-4">
                  <div className="text-2xl font-black text-cyan-200">{metric}</div>
                  <div className="mt-1 text-xs uppercase tracking-wide text-slate-400">{label}</div>
                </div>
              ))}
            </div>
          </div>
          <div className="relative">
            <div className="relative aspect-[4/3] rounded-2xl border border-white/10 bg-white/[0.06] p-4 shadow-2xl shadow-cyan-950/40 overflow-hidden">
              <img src={heroImage} alt="PRISM analytics dashboard preview" className="absolute inset-4 h-[calc(100%-2rem)] w-[calc(100%-2rem)] rounded-xl object-cover opacity-25" />
              <Canvas shadows camera={{ position: [0, 0, 7], fov: 45 }} className="relative z-10">
                <ambientLight intensity={0.7} />
                <directionalLight position={[4, 5, 6]} intensity={3.5} castShadow />
                <pointLight position={[-4, 2, 3]} intensity={5} color="#a855f7" />
                <pointLight position={[4, -1, 3]} intensity={4} color="#2563eb" />
                <pointLight position={[1, 4, -2]} intensity={3} color="#ec4899" />
                <Stars radius={100} depth={50} count={1600} factor={3} saturation={0} fade speed={0.4} />
                <Environment preset="night" />
                <PrismMesh />
                <ContactShadows position={[1.8, -1.1, 0]} opacity={0.5} scale={5} blur={2.5} far={4} />
                <OrbitControls enablePan={false} enableZoom={false} enableDamping dampingFactor={0.08} autoRotate autoRotateSpeed={0.8} />
              </Canvas>
            </div>
          </div>
        </div>
      </section>

      {/* 
        ========================================================================
        PROBLEM VS SOLUTION (Asymmetrical Layout)
        ========================================================================
      */}
      <section id="problem" className="py-24 px-6 max-w-7xl mx-auto">
        <div className="grid md:grid-cols-2 gap-20 items-center">
          <div className="space-y-6 md:pr-12">
            <h2 className="text-sm font-mono text-blue-500 uppercase tracking-widest">The Divide</h2>
            <h3 className="text-4xl font-semibold leading-tight">Students dream. Parents pay.<br/>The result is conflict.</h3>
            <p className="text-gray-600 leading-relaxed text-lg">
              Currently, 90% of students choose careers based on hearsay. Traditional counseling ignores the family's financial constraints, leading to massive student debt and intense parent-student conflict.
            </p>
          </div>
          <div className="bg-blue-500 text-white p-12 rounded-3xl shadow-2xl md:translate-y-12">
            <h2 className="text-sm font-mono text-blue-200 uppercase tracking-widest mb-6">The Solution</h2>
            <p className="text-xl font-light leading-relaxed mb-8">
              We vectorize student psychometrics and map them against parental financial limits. Our deterministic math generates affordable, conflict-free STEAM pathways.
            </p>
            <ul className="space-y-4 font-mono text-sm">
              <li className="flex items-center gap-3"><Database size={16} /> O*NET 31.0 Authentic Datasets</li>
              <li className="flex items-center gap-3"><Code size={16} /> Deterministic EMI & ROI Solvers</li>
              <li className="flex items-center gap-3"><BrainCircuit size={16} /> Parent-Student Conflict Index (PSCI)</li>
            </ul>
          </div>
        </div>
      </section>

      {/* 
        ========================================================================
        ARCHITECTURE & TECH STACK
        ========================================================================
      */}
      <section id="architecture" className="py-32 bg-gray-50 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-20">
            <h2 className="text-sm font-mono text-blue-500 uppercase tracking-widest mb-4">Architecture</h2>
            <h3 className="text-4xl font-bold text-gray-900">Powered by Math. Explained by AI.</h3>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              { title: "React + Tailwind", desc: "Interactive psychometric crisis simulation replacing static surveys.", icon: <Code size={32} /> },
              { title: "FastAPI + SQLite", desc: "SQLite-backed career, exam, scholarship and demand store with JSON fallback.", icon: <Database size={32} /> },
              { title: "Gemini + Live Scraper", desc: "Gemini 1.5 Flash counseling plus BeautifulSoup market pulse with cached fallback.", icon: <BrainCircuit size={32} /> }
            ].map((tech, i) => (
              <div key={i} className="bg-white p-10 rounded-2xl shadow-sm border border-gray-100 hover:shadow-xl transition-shadow duration-300">
                <div className="text-blue-500 mb-6">{tech.icon}</div>
                <h4 className="text-xl font-bold mb-3">{tech.title}</h4>
                <p className="text-gray-600">{tech.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* 
        ========================================================================
        TEAM FOUR SPADES
        ========================================================================
      */}
      <section id="team" className="py-32 px-6 max-w-7xl mx-auto text-center">
        <h2 className="text-sm font-mono text-blue-500 uppercase tracking-widest mb-4">Meet The Creators</h2>
        <h3 className="text-4xl font-bold mb-16">Team Four Spades</h3>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
          {["Palanivel Rajan S", "Sanjeev D", "PG Navin Kumar", "M Yashwant"].map((member, i) => (
            <div key={i} className="flex flex-col items-center">
              <div className="w-24 h-24 bg-gray-100 rounded-full mb-6 flex items-center justify-center text-gray-400">
                <Users size={32} />
              </div>
              <h5 className="font-semibold">{member}</h5>
              <p className="text-sm text-gray-500 font-mono mt-2">DQNM</p>
            </div>
          ))}
        </div>
      </section>

      {/* 
        ========================================================================
        SPONSORS
        ========================================================================
      */}
      <section className="py-12 bg-white border-t border-gray-100">
        <div className="max-w-7xl mx-auto px-6 text-center">
          <h4 className="text-xs font-mono text-gray-400 uppercase tracking-widest mb-6">Proudly Supported By</h4>
          <div className="flex justify-center items-center opacity-70 hover:opacity-100 transition-opacity duration-300">
            <img src="/sponsors.png" alt="Hackathon Sponsors" className="max-h-16 md:max-h-20 object-contain grayscale hover:grayscale-0 transition-all duration-500" />
          </div>
        </div>
      </section>

      {/* 
        ========================================================================
        STICKY FOOTER CTA
        ========================================================================
      */}
      <footer className="sticky bottom-0 w-full bg-white border-t border-gray-100 p-4 z-40 shadow-[0_-10px_40px_rgba(0,0,0,0.05)]">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row justify-between items-center gap-4">
          <div className="font-mono text-sm text-gray-500">
            Status: <span className="text-green-500">System Online</span>
          </div>
          <button 
            onClick={() => navigate('/assessment')}
            className="w-full sm:w-auto px-8 py-4 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-xl flex items-center justify-center gap-3 transition-colors shadow-lg"
          >
            INITIALIZE SIMULATION <ChevronRight size={20} />
          </button>
        </div>
      </footer>

      {/* Back to Top Button */}
      <button 
        onClick={scrollToTop}
        className={`fixed right-6 bottom-24 p-3 bg-gray-900 text-white rounded-full shadow-lg transition-all duration-300 ${showBackToTop ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10 pointer-events-none'}`}
      >
        <ArrowUp size={20} />
      </button>

    </div>
  );
};

export default LandingPage;
