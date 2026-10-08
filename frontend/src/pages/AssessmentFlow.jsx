import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import prismBg from '../assets/prism-bg.jpg';

const missions = [
  {
    id: 1,
    type: 'text',
    tag: 'Decision Mission',
    title: "Your college's main building has lost power, and classes are disrupted.",
    subtitle: "You have 10 minutes and a limited budget of ₹10,000 to find the cause and propose a solution. What would you do first?",
    options: [
      { id: 'A', text: 'Inspect the electrical panels and get technical details.', icon: '🔍', trait: 'investigative' },
      { id: 'B', text: 'Talk to the facility staff or ask an expert for advice.', icon: '👥', trait: 'social' },
      { id: 'C', text: 'Check the power usage data and analyse the pattern.', icon: '📊', trait: 'conventional' },
      { id: 'D', text: 'Look for a temporary fix and start the repair work.', icon: '🔧', trait: 'realistic' }
    ],
    hint: "There's no single 'right' answer. We're tracking how you think, what you choose and how you solve problems."
  },
  {
    id: 2,
    type: 'image',
    tag: 'Design Challenge',
    title: "You need to design a mobile app screen for a student who is struggling to manage assignments.",
    subtitle: "Which design feels most effective and user-friendly?",
    options: [
      { id: 'A', image: 'https://picsum.photos/seed/prism1/400/300', text: 'Clean List & Minimalist', trait: 'conventional' },
      { id: 'B', image: 'https://picsum.photos/seed/prism2/400/300', text: 'Dark Mode & Focused', trait: 'investigative' },
      { id: 'C', image: 'https://picsum.photos/seed/prism3/400/300', text: 'Calendar & Vibrant', trait: 'artistic' },
      { id: 'D', image: 'https://picsum.photos/seed/prism4/400/300', text: 'Dashboard & Metrics', trait: 'enterprising' }
    ],
    hint: "We're observing your preferences, creativity, and attention to detail."
  },
  {
    id: 3,
    type: 'text',
    tag: 'Crisis Mission',
    title: "Your team's project deadline is tomorrow, but a critical bug just appeared.",
    subtitle: "The entire system crashes when users try to log in. How do you handle it?",
    options: [
      { id: 'A', text: 'Dive straight into the codebase and debug the logic.', icon: '💻', trait: 'investigative' },
      { id: 'B', text: 'Organize a quick meeting to distribute tasks.', icon: '📅', trait: 'enterprising' },
      { id: 'C', text: 'Write a creative workaround to bypass the login temporarily.', icon: '✨', trait: 'artistic' },
      { id: 'D', text: 'Follow the standard rollback procedure to the last stable version.', icon: '📋', trait: 'conventional' }
    ],
    hint: "Every choice maps to a different psychological archetype."
  },
  {
    id: 4,
    type: 'text',
    tag: 'Parent Constraint Module',
    title: "To give you realistic paths, we need your family's budget.",
    subtitle: "What is the maximum budget your family can comfortably allocate for your higher education?",
    options: [
      { id: 'A', text: 'Under ₹5 Lakhs (Looking for Gov/Subsidized)', icon: '🏛️', value: { max: 500000, tol: 200000 } },
      { id: 'B', text: '₹5 - ₹12 Lakhs (Standard Private)', icon: '📘', value: { max: 1200000, tol: 500000 } },
      { id: 'C', text: '₹12 - ₹25 Lakhs (Premium Private)', icon: '🏢', value: { max: 2500000, tol: 1000000 } },
      { id: 'D', text: 'Over ₹25 Lakhs (Open to Abroad/Tier 1)', icon: '🌍', value: { max: 5000000, tol: 2000000 } }
    ],
    hint: "This prevents PRISM from recommending pathways that cause financial strain."
  },
  {
    id: 5,
    type: 'text',
    tag: 'Mobility & Geographic Module',
    title: "Where are you willing to study?",
    subtitle: "Select your geographic mobility preference.",
    options: [
      { id: 'A', text: 'My Own City Only (Commuter)', icon: '🏠', value: 'own_city' },
      { id: 'B', text: 'My Home State', icon: '📍', value: 'own_state' },
      { id: 'C', text: 'Anywhere in India', icon: '🇮🇳', value: 'any_india' },
      { id: 'D', text: 'Open to Studying Abroad', icon: '✈️', value: 'abroad' }
    ],
    hint: "Finalizing your physical boundaries for accurate map generation..."
  },
  {
    id: 6,
    type: 'text',
    tag: 'Parent Review',
    title: "Parent review: what matters most for approval?",
    subtitle: "This final parent checkpoint calibrates PSCI and the final pathway ranking.",
    options: [
      { id: 'A', text: 'Lowest loan and maximum affordability', icon: '💰', value: { risk: 2, salary: 0.25, stability: 0.55, prestige: 0.15, passion: 0.05 } },
      { id: 'B', text: 'Stable salary and safe career growth', icon: '🛡️', value: { risk: 3, salary: 0.35, stability: 0.45, prestige: 0.15, passion: 0.05 } },
      { id: 'C', text: 'Prestige, brand value, and top institutions', icon: '🏛️', value: { risk: 4, salary: 0.30, stability: 0.25, prestige: 0.40, passion: 0.05 } },
      { id: 'D', text: 'Support the student passion if ROI is reasonable', icon: '🤝', value: { risk: 4, salary: 0.30, stability: 0.25, prestige: 0.15, passion: 0.30 } }
    ],
    hint: "This is the parent-side review before PRISM generates the final report."
  }
];

const AssessmentFlow = () => {
  const navigate = useNavigate();
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const containerRef = useRef(null);
  const questionRefs = useRef([]);

  const handleSelect = (missionId, optionId, data) => {
    if (answers[missionId]) return;

    setAnswers(prev => ({ ...prev, [missionId]: { optionId, data } }));

    setTimeout(() => {
      if (currentIndex < missions.length - 1) {
        setCurrentIndex(prev => prev + 1);
        setTimeout(() => {
          questionRefs.current[currentIndex + 1]?.scrollIntoView({
            behavior: 'smooth',
            block: 'center'
          });
        }, 100);
      } else {
        submitAssessment({ ...answers, [missionId]: { optionId, data } });
      }
    }, 600);
  };

  const submitAssessment = async (finalAnswers) => {
    setIsSubmitting(true);
    
    let r=3, i=3, a=3, s=3, e=3, c=3;
    
    // Parse traits from first 3 questions
    [1, 2, 3].forEach(id => {
      const trait = finalAnswers[id]?.data;
      if (trait === 'realistic') r+=2;
      if (trait === 'investigative') i+=2;
      if (trait === 'artistic') a+=2;
      if (trait === 'social') s+=2;
      if (trait === 'enterprising') e+=2;
      if (trait === 'conventional') c+=2;
    });

    const budgetData = finalAnswers[4]?.data || { max: 1500000, tol: 1000000 };
    const locationData = finalAnswers[5]?.data || 'any_india';
    const parentReview = finalAnswers[6]?.data || { risk: 3, prestige: 0.4, salary: 0.4, stability: 0.2, passion: 0.0 };

    const payload = {
      student_form: {
        name: "Explorer",
        riasec: [r, i, a, s, e, c],
        aptitude: [4, 4, 4, 4],
        domain_prefs: { "engineering": 5, "medicine": 3, "design": 4, "commerce": 3, "law": 3, "social_science": 3, "pure_science": 3, "arts": 3, "management": 3, "education": 3, "agriculture": 3, "emerging_tech": 3 },
        risk_appetite: 4,
        location: locationData,
        city: 'Chennai',
        state: 'Tamil Nadu',
        country: locationData === 'abroad' ? 'Singapore' : 'India',
        work_style: ["research", "creative"]
      },
      parent_form: {
        domain_prefs: { "engineering": 5, "medicine": 4, "design": 3, "commerce": 3, "law": 3, "social_science": 3, "pure_science": 3, "arts": 3, "management": 3, "education": 3, "agriculture": 3, "emerging_tech": 3 },
        risk_appetite: parentReview.risk,
        location: locationData,
        budget_max_no_loan: budgetData.max,
        loan_tolerance: budgetData.tol,
        priority_weights: { "prestige": parentReview.prestige, "salary": parentReview.salary, "stability": parentReview.stability, "passion": parentReview.passion }
      },
      institution_type: "private"
    };

    try {
      const response = await axios.post('http://localhost:8000/analyze', payload);
      navigate('/results', { state: { engineOutput: response.data, student_profile: payload.student_form, parent_profile: payload.parent_form } });
    } catch (error) {
      console.error(error);
      alert("Failed to submit. Check backend.");
      setIsSubmitting(false);
    }
  };

  return (
    <div
      className="min-h-screen bg-[#070b14] bg-fixed bg-cover bg-center bg-blend-overlay text-white font-sans overflow-x-hidden selection:bg-indigo-500/30"
      style={{ backgroundImage: `linear-gradient(rgba(7,11,20,.84), rgba(7,11,20,.9)), url(${prismBg})` }}
      ref={containerRef}
    >
      
      {/* Top Navigation */}
      <div className="fixed top-0 left-0 w-full z-50 bg-[#070b14]/80 backdrop-blur-md border-b border-white/10 px-6 py-4 flex justify-between items-center shadow-lg shadow-indigo-950/20">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-gradient-to-tr from-indigo-600 to-cyan-400 rounded-lg flex items-center justify-center font-bold shadow-lg shadow-cyan-500/30">
            ▲
          </div>
          <div>
            <h1 className="text-sm font-bold tracking-wider">Career Discovery Lab</h1>
            <p className="text-xs text-indigo-300">Explore • Solve • Discover</p>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <span className="text-xs font-mono text-cyan-400 font-bold bg-cyan-950/50 px-3 py-1 rounded-full border border-cyan-800">
            Mission {Math.min(currentIndex + 1, missions.length)} / {missions.length}
          </span>
          <div className="w-32 h-2.5 bg-gray-800 rounded-full overflow-hidden shadow-inner">
            <motion.div 
              className="h-full bg-gradient-to-r from-cyan-400 to-emerald-400"
              initial={{ width: 0 }}
              animate={{ width: `${((currentIndex) / missions.length) * 100}%` }}
              transition={{ duration: 0.5 }}
            />
          </div>
        </div>
      </div>

      <div className="pt-32 pb-64 max-w-4xl mx-auto px-4 relative flex flex-col items-center">
        
        {/* Background Winding Line */}
        <div className="absolute top-0 bottom-0 left-1/2 -translate-x-1/2 w-1.5 bg-gray-800/80 rounded-full z-0 hidden md:block">
          <motion.div 
            className="w-full bg-gradient-to-b from-cyan-400 via-indigo-500 to-emerald-400 rounded-full"
            initial={{ height: 0 }}
            animate={{ height: `${((currentIndex + 0.5) / missions.length) * 100}%` }}
            transition={{ duration: 0.8, ease: "easeInOut" }}
            style={{ filter: 'drop-shadow(0 0 10px rgba(99, 102, 241, 0.8))' }}
          />
        </div>

        {missions.map((mission, index) => {
          const isCompleted = index < currentIndex;
          const isActive = index === currentIndex;
          const isLocked = index > currentIndex;
          
          const alignment = index % 2 === 0 ? 'md:pr-24 md:text-right md:items-end' : 'md:pl-24 md:text-left md:items-start';
          
          return (
            <div 
              key={mission.id} 
              ref={el => questionRefs.current[index] = el}
              className={`relative w-full flex flex-col items-center md:items-stretch ${alignment} mb-24 z-10 transition-all duration-700 ${isLocked ? 'opacity-40 blur-[2px] pointer-events-none scale-95' : 'opacity-100 scale-100'}`}
              style={{ minHeight: '40vh', justifyContent: 'center' }}
            >
              
              {/* Path Checkpoint Dot (Tiny in the middle of the line) */}
              <div className={`hidden absolute top-1/2 -translate-y-1/2 left-1/2 -translate-x-1/2 w-6 h-6 rounded-full md:flex items-center justify-center transition-all duration-500 z-20 ${
                isCompleted ? 'bg-emerald-500 border-4 border-[#070b14]' : 
                isActive ? 'bg-cyan-400 border-4 border-[#070b14] shadow-[0_0_15px_rgba(34,211,238,0.8)]' : 
                'bg-gray-800 border-4 border-[#070b14]'
              }`}>
                {isCompleted && <span className="text-[10px] font-black text-[#070b14]">✓</span>}
              </div>

              {/* Mission Card */}
              <motion.div 
                className={`w-full md:w-4/5 max-w-2xl bg-white/[0.03] backdrop-blur-xl border border-white/10 pt-10 px-6 pb-6 md:p-8 rounded-3xl shadow-2xl relative overflow-hidden transition-all duration-300 ${
                  isActive ? 'ring-2 ring-indigo-500/50 shadow-[0_0_40px_rgba(79,70,229,0.15)]' : ''
                }`}
                initial={{ opacity: 0, y: 50 }}
                animate={{ 
                  opacity: isLocked ? 0.4 : 1, 
                  y: 0, 
                  filter: isCompleted ? 'grayscale(0.6)' : 'grayscale(0)'
                }}
                transition={{ duration: 0.5 }}
              >
                
                {/* Number Badge MOVED TO CORNER */}
                <div className={`absolute top-0 left-0 w-12 h-12 rounded-br-2xl flex items-center justify-center font-black text-lg transition-all duration-500 shadow-lg ${
                  isCompleted ? 'bg-emerald-500 text-[#070b14]' :
                  isActive ? 'bg-gradient-to-br from-cyan-400 to-indigo-500 text-white shadow-cyan-500/50' :
                  'bg-gray-800 text-gray-500'
                }`}>
                  {isCompleted ? '✓' : mission.id}
                </div>

                {/* Glow effect inside card */}
                {isActive && <div className="absolute -top-32 -right-32 w-64 h-64 bg-indigo-500/20 rounded-full blur-[80px] pointer-events-none" />}

                <div className={`inline-flex items-center gap-2 px-3 py-1.5 bg-white/10 rounded-full text-xs font-bold mb-6 ml-10 ${isActive ? 'text-cyan-300' : 'text-gray-400'}`}>
                  {isActive && <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse shadow-[0_0_8px_#22d3ee]" />}
                  {mission.tag}
                </div>

                <h2 className="text-2xl md:text-3xl font-bold text-white mb-3 leading-tight">{mission.title}</h2>
                <p className="text-indigo-200/70 mb-8">{mission.subtitle}</p>

                {mission.type === 'text' ? (
                  <div className="grid grid-cols-1 gap-3">
                    {mission.options.map(opt => {
                      const isSelected = answers[mission.id]?.optionId === opt.id;
                      return (
                        <button
                          key={opt.id}
                          onClick={() => handleSelect(mission.id, opt.id, opt.value || opt.trait)}
                          disabled={isCompleted || isLocked}
                          className={`w-full text-left p-4 rounded-2xl border transition-all duration-300 flex items-center gap-4 group
                            ${isSelected 
                              ? 'bg-emerald-500/20 border-emerald-500/60 ring-2 ring-emerald-500/50 shadow-[0_0_15px_rgba(16,185,129,0.2)]' 
                              : 'bg-white/[0.04] border-white/10 hover:bg-white/[0.08] hover:border-indigo-400/40 hover:-translate-y-1'}
                          `}
                        >
                          <div className={`w-10 h-10 rounded-full flex items-center justify-center text-lg font-bold shrink-0 transition-colors ${
                            isSelected ? 'bg-emerald-500 text-white' : 'bg-indigo-900/50 text-indigo-300 group-hover:bg-indigo-500 group-hover:text-white'
                          }`}>
                            {opt.id}
                          </div>
                          <div className="flex-1">
                            <span className={`font-medium text-sm md:text-base ${isSelected ? 'text-emerald-100' : 'text-gray-200 group-hover:text-white'}`}>{opt.text}</span>
                          </div>
                          <div className="text-2xl opacity-50 group-hover:scale-110 transition-transform">{opt.icon}</div>
                        </button>
                      );
                    })}
                  </div>
                ) : (
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    {mission.options.map(opt => {
                      const isSelected = answers[mission.id]?.optionId === opt.id;
                      return (
                        <button
                          key={opt.id}
                          onClick={() => handleSelect(mission.id, opt.id, opt.value || opt.trait)}
                          disabled={isCompleted || isLocked}
                          className={`relative overflow-hidden rounded-2xl border-2 transition-all duration-300 group aspect-[4/3]
                            ${isSelected ? 'border-emerald-500 ring-4 ring-emerald-500/30' : 'border-white/10 hover:border-indigo-400 hover:-translate-y-1 hover:shadow-xl'}
                          `}
                        >
                          <img src={opt.image} alt="Option" className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110" />
                          <div className="absolute inset-0 bg-gradient-to-t from-[#070b14]/90 via-[#070b14]/30 to-transparent" />
                          <div className={`absolute top-3 left-3 w-8 h-8 rounded-full flex items-center justify-center font-bold backdrop-blur-md shadow-lg ${
                            isSelected ? 'bg-emerald-500 text-white' : 'bg-black/60 text-white'
                          }`}>
                            {opt.id}
                          </div>
                          <div className="absolute bottom-4 left-4 right-4 text-left">
                            <span className="font-bold text-white text-sm tracking-wide">{opt.text}</span>
                          </div>
                        </button>
                      );
                    })}
                  </div>
                )}

                <div className="mt-8 pt-5 border-t border-white/10 flex items-start gap-3 opacity-60">
                  <span className="text-yellow-400 text-lg">💡</span>
                  <p className="text-xs text-gray-400 leading-relaxed font-mono">{mission.hint}</p>
                </div>
              </motion.div>
            </div>
          );
        })}

      </div>

      {/* Loading Overlay */}
      <AnimatePresence>
        {isSubmitting && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="fixed inset-0 bg-[#070b14]/90 backdrop-blur-xl z-[100] flex flex-col items-center justify-center"
          >
            <div className="w-24 h-24 relative mb-8">
              <div className="absolute inset-0 border-4 border-indigo-500/20 rounded-full"></div>
              <div className="absolute inset-0 border-4 border-cyan-400 rounded-full border-t-transparent animate-spin"></div>
            </div>
            <h2 className="text-3xl font-bold text-white mb-4 tracking-tight">Vectorizing Psychometrics...</h2>
            <p className="text-indigo-300 font-mono text-sm max-w-sm text-center">Crunching parent constraints and career metrics</p>
          </motion.div>
        )}
      </AnimatePresence>

    </div>
  );
};

export default AssessmentFlow;
