import React, { useState, useEffect, useRef } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import axios from 'axios';
import {
  Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  ResponsiveContainer, Tooltip as RechartsTooltip, Legend,
  ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, ReferenceLine, ZAxis, Cell
} from 'recharts';
import 'leaflet/dist/leaflet.css';
import prismBg from '../assets/prism-bg.jpg';

// ─── Helpers ─────────────────────────────────────────────────────────────────
const fmt = (n) => isFinite(n) && n > 0 ? `₹${Number(n).toLocaleString('en-IN')}` : '₹0';
const pct = (n) => isFinite(n) ? `${Math.round(n * 100)}%` : 'N/A';
const round2 = (n) => isFinite(n) ? Number(n).toFixed(2) : 'N/A';

// ─── PDF print styles ─────────────────────────────────────────────────────────
const PDF_STYLE = `
.print-only { display: none; }
@media print {
  @page { size: A4; margin: 10mm; }
  html, body { background: white !important; color: black !important; }
  .no-print, .print-skip, .screen-only { display: none !important; }
  .print-only {
    display: block !important;
    font-family: Arial, sans-serif;
    color: #111827 !important;
    font-size: 12px;
    line-height: 1.45;
  }
  .pdf-title {
    background: #0f172a !important;
    color: #ffffff !important;
    padding: 14px 16px;
    border-radius: 8px;
    margin-bottom: 14px;
  }
  .pdf-title h1 { color: #ffffff !important; margin: 0 0 4px; font-size: 24px; }
  .pdf-title p { color: #cbd5e1 !important; margin: 0; }
  .pdf-metrics { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin-bottom: 16px; }
  .pdf-metric { border: 1px solid #cbd5e1; border-radius: 8px; padding: 10px; background: #f8fafc !important; }
  .pdf-metric b { display: block; color: #475569 !important; font-size: 10px; text-transform: uppercase; margin-bottom: 4px; }
  .pdf-metric span { color: #0f172a !important; font-size: 15px; font-weight: 800; }
  .pdf-section-title { font-size: 15px; color: #0f172a !important; margin: 14px 0 8px; border-bottom: 2px solid #0f172a; padding-bottom: 4px; }
  .pdf-table { width: 100%; border-collapse: collapse; margin-bottom: 12px; table-layout: fixed; }
  .pdf-table th { background: #e2e8f0 !important; color: #0f172a !important; border: 1px solid #94a3b8; padding: 7px; font-size: 10px; text-transform: uppercase; }
  .pdf-table td { color: #111827 !important; border: 1px solid #cbd5e1; padding: 7px; vertical-align: top; }
  .pdf-note { border: 1px solid #cbd5e1; border-left: 4px solid #10b981; padding: 10px; background: #f8fafc !important; margin-bottom: 12px; }
  .pdf-note, .pdf-note * { color: #111827 !important; }
  .pdf-list { margin: 0; padding-left: 18px; }
  .pdf-list li { margin-bottom: 4px; color: #111827 !important; }
  .print-card {
    background: white !important;
    border: 1px solid #d1d5db !important;
    color: black !important;
    break-inside: avoid;
    page-break-inside: avoid;
    box-shadow: none !important;
  }
  .print-card * { color: black !important; background: transparent !important; box-shadow: none !important; }
  .print-grid { display: block !important; padding: 0 !important; }
  .print-main { width: 100% !important; max-width: 100% !important; }
  .print-compact { margin-bottom: 8px !important; }
}`;

export default function ResultsDashboard() {
  const location = useLocation();
  const navigate = useNavigate();
  const reportRef = useRef(null);

  const rawOutput = location.state?.engineOutput || {};
  const studentProfile = location.state?.student_profile || {};
  const parentProfile = location.state?.parent_profile || {};

  const topCareers = rawOutput.top_careers || [];
  const conflict = rawOutput.conflict || {};
  const swot = rawOutput.swot || {};
  const roadmap = rawOutput.roadmap || {};
  const compromise = rawOutput.compromise_careers || [];

  // ── Derive display careers ─────────────────────────────────────────────────
  const displayCareers = topCareers.map((c) => {
    const fin = c.financial_detail || {};
    const fit = c.fit_detail || {};
    return {
      id: c.career_id || 'unknown',
      title: fit.career_label || c.career_id?.replace(/_/g, ' ') || 'Unknown',
      fitPct: Math.round((c.fit_score || 0) * 100),
      demandPct: Math.round((c.demand_score || 0) * 100),
      emi: fin.monthly_emi || 0,
      roi: fin.roi || 0,
      payback: fin.payback_years || 0,
      status: (fin.status || 'UNKNOWN').replace(/_/g, ' '),
      composite: c.composite_score || 0,
      skills: fit.skills || [],
      hotspots: fit.geo_hotspots || [],
      affordable: Boolean(c.affordable || fin.affordable),
    };
  });

  const affordableCareers = displayCareers.filter(c => c.affordable);
  const pathwayCareers = [
    ...affordableCareers,
    ...displayCareers.filter(c => !c.affordable),
  ].slice(0, 3);
  const top = pathwayCareers[0] || displayCareers[0] || {};
  const avgEmi = displayCareers.length ? displayCareers.reduce((a, c) => a + c.emi, 0) / displayCareers.length : 15000;
  const avgRoi = displayCareers.length ? displayCareers.reduce((a, c) => a + c.roi, 0) / displayCareers.length : 3;
  const bestValue = top;
  const scholarships = roadmap.scholarships || [];

  // ── Chat ──────────────────────────────────────────────────────────────────
  const [chatMessages, setChatMessages] = useState([
    { sender: 'bot', text: 'Hi! I am your PRISM AI counselor. Ask me anything about your career pathway.' }
  ]);
  const [chatInput, setChatInput] = useState('');
  const [chatLoading, setChatLoading] = useState(false);
  const [language, setLanguage] = useState('English');
  const [apiHealth, setApiHealth] = useState(null);
  const [liveMarket, setLiveMarket] = useState(null);

  useEffect(() => {
    axios.get('http://localhost:8000/health')
      .then(r => setApiHealth(r.data))
      .catch(() => setApiHealth({ status: 'offline', data_source: 'unknown' }));
  }, []);

  useEffect(() => {
    if (!top.id) return;
    axios.get(`http://localhost:8000/live-market/${top.id}`)
      .then(r => setLiveMarket(r.data))
      .catch(() => setLiveMarket(null));
  }, [top.id]);

  // ── Map geolocation ────────────────────────────────────────────────────────
  const [userCoords, setUserCoords] = useState(null);
  const [mapQuery, setMapQuery] = useState('');
  const mapRef = useRef(null);
  const leafletMap = useRef(null);

  const locationLabel = (() => {
    const mobility = studentProfile.location || 'any_india';
    if (mobility === 'own_city') return `${studentProfile.city || 'Chennai'}, ${studentProfile.state || 'Tamil Nadu'}`;
    if (mobility === 'own_state') return `${studentProfile.state || 'Tamil Nadu'}, India`;
    if (mobility === 'abroad') return studentProfile.country || 'Singapore';
    return 'India';
  })();
  const mapTerm = `${top.title || 'career'} colleges`;
  const mapSearch = `${mapTerm} near ${locationLabel}`;
  const mapEmbedUrl = `https://maps.google.com/maps?q=${encodeURIComponent(mapSearch)}&t=&z=11&ie=UTF8&iwloc=&output=embed`;
  const mapOpenUrl = `https://www.google.com/maps/search/${encodeURIComponent(mapSearch)}`;

  useEffect(() => {
    const coords = {
      own_city: { lat: 13.0827, lng: 80.2707 },
      own_state: { lat: 11.1271, lng: 78.6569 },
      any_india: { lat: 20.5937, lng: 78.9629 },
      abroad: { lat: 1.3521, lng: 103.8198 },
    };
    setUserCoords(coords[studentProfile.location || 'any_india'] || coords.any_india);
  }, [studentProfile.location]);

  // Build Leaflet map once coords & career known
  useEffect(() => {
    if (!userCoords || !top.title || !mapRef.current) return;
    if (leafletMap.current) return; // Already initialized

    // Dynamically load leaflet CSS
    if (!document.getElementById('leaflet-css')) {
      const link = document.createElement('link');
      link.id = 'leaflet-css';
      link.rel = 'stylesheet';
      link.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css';
      document.head.appendChild(link);
    }

    import('leaflet').then((L) => {
      const map = L.map(mapRef.current).setView([userCoords.lat, userCoords.lng], 11);
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 18,
      }).addTo(map);

      // User location marker
      const userIcon = L.divIcon({
        html: '<div style="background:#6366f1;width:16px;height:16px;border-radius:50%;border:3px solid white;box-shadow:0 0 8px #6366f1;"></div>',
        className: '', iconAnchor: [8, 8],
      });
      L.marker([userCoords.lat, userCoords.lng], { icon: userIcon })
        .addTo(map)
        .bindPopup(`<b>${locationLabel}</b><br/>Selected mobility target`).openPopup();

      // Build Nominatim search for nearby colleges
      const category = top.title.toLowerCase();
      let amenityQuery = 'university';
      if (category.includes('medical') || category.includes('doctor') || category.includes('nurse')) amenityQuery = 'college;hospital';
      if (category.includes('design') || category.includes('architect')) amenityQuery = 'college';

      const nominatimUrl = `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(top.title + ' college university ' + locationLabel)}&format=json&limit=10&addressdetails=1`;

      fetch(nominatimUrl, { headers: { 'Accept-Language': 'en' } })
        .then(r => r.json())
        .then(results => {
          const colIcon = L.divIcon({
            html: '<div style="background:#10b981;width:14px;height:14px;border-radius:50%;border:2px solid white;box-shadow:0 0 6px #10b981;"></div>',
            className: '', iconAnchor: [7, 7],
          });
          results.forEach(place => {
            L.marker([parseFloat(place.lat), parseFloat(place.lon)], { icon: colIcon })
              .addTo(map)
              .bindPopup(`<b>${place.display_name.split(',')[0]}</b><br/><small>${place.display_name.split(',').slice(1, 3).join(',')}</small>`);
          });
          if (results.length > 0) {
            const bounds = L.latLngBounds(
              results.map(p => [parseFloat(p.lat), parseFloat(p.lon)])
            );
            bounds.extend([userCoords.lat, userCoords.lng]);
            map.fitBounds(bounds, { padding: [40, 40] });
          }
        })
        .catch(() => {});

      // Also drop pins on known hotspots from career data
      (top.hotspots || []).forEach(city => {
        const cityCoords = {
          'Bangalore': [12.9716, 77.5946], 'Mumbai': [19.0760, 72.8777],
          'Delhi': [28.7041, 77.1025], 'Hyderabad': [17.3850, 78.4867],
          'Chennai': [13.0827, 80.2707], 'Pune': [18.5204, 73.8567],
          'Kolkata': [22.5726, 88.3639], 'Ahmedabad': [23.0225, 72.5714],
        };
        if (cityCoords[city]) {
          const hotIcon = L.divIcon({
            html: `<div style="background:#f59e0b;padding:3px 6px;border-radius:8px;font-size:10px;font-weight:bold;color:#000;white-space:nowrap;box-shadow:0 2px 4px rgba(0,0,0,0.3);">${city}</div>`,
            className: '', iconAnchor: [20, 8],
          });
          L.marker(cityCoords[city], { icon: hotIcon }).addTo(map)
            .bindPopup(`<b>${city}</b><br/>High demand for ${top.title}`);
        }
      });

      leafletMap.current = map;
    });
  }, [userCoords, top.title]);

  const sendChat = async () => {
    if (!chatInput.trim()) return;
    const msg = chatInput;
    setChatMessages(p => [...p, { sender: 'user', text: msg }]);
    setChatInput('');
    setChatLoading(true);
    try {
      const r = await axios.post('http://localhost:8000/chat', {
        engine_output: rawOutput,
        student_profile: studentProfile,
        parent_profile: parentProfile,
        user_message: msg,
        language,
        history: []
      });
      setChatMessages(p => [...p, { sender: 'bot', text: r.data?.response || 'Response received.' }]);
    } catch {
      setChatMessages(p => [...p, { sender: 'bot', text: '⚠️ Backend offline. Restart with: python -m uvicorn api.main:app --port 8000' }]);
    } finally {
      setChatLoading(false);
    }
  };

  const downloadPDF = () => {
    window.print();
  };

  // ── RIASEC Radar data ──────────────────────────────────────────────────────
  const riasec = studentProfile.riasec || [3, 3, 3, 3, 3, 3];
  const radarData = ['Realistic', 'Investigative', 'Artistic', 'Social', 'Enterprising', 'Conventional'].map((s, i) => ({
    subject: s,
    student: Math.round((riasec[i] || 3) * 20),
    benchmark: Math.round((top.fitPct || 75) + (i % 2 === 0 ? 5 : -5)),
    fullMark: 100,
  }));

  // ── Conflict color helpers ─────────────────────────────────────────────────
  const conflictSev = conflict.severity || 'UNKNOWN';
  const psciScore = Math.round((conflict.conflict_index || 0) * 100);
  const sevColor = { LOW: '#10b981', MODERATE: '#f59e0b', HIGH: '#ef4444' }[conflictSev] || '#6b7280';
  const parentRisk = parentProfile.risk_appetite > 1 ? `${parentProfile.risk_appetite}/5` : `${Math.round((parentProfile.risk_appetite || 0) * 100)}%`;

  // ── Quadrant zone color ─────────────────────────────────────────────────────
  const zoneColor = (emi, roi) => {
    if (emi < avgEmi && roi >= avgRoi) return '#10b981';
    if (emi >= avgEmi && roi >= avgRoi) return '#3b82f6';
    if (emi < avgEmi && roi < avgRoi) return '#f59e0b';
    return '#ef4444';
  };

  return (
    <>
      <style>{PDF_STYLE}</style>
      <div
        className="min-h-screen text-white font-sans bg-[#070b14] bg-fixed bg-cover bg-center bg-blend-overlay"
        style={{ backgroundImage: `linear-gradient(rgba(7,11,20,.82), rgba(7,11,20,.9)), url(${prismBg})` }}
        ref={reportRef}
      >
        <section className="print-only">
          <div className="pdf-title">
            <h1>PRISM Parent Report</h1>
            <p>Career, cost and family-fit summary for {studentProfile.name || 'Explorer'}.</p>
          </div>
          <div className="pdf-metrics">
            <div className="pdf-metric"><b>Top Match</b><span>{top.title || 'Pending'}</span></div>
            <div className="pdf-metric"><b>PSCI</b><span>{psciScore}/100 ({conflictSev})</span></div>
            <div className="pdf-metric"><b>Monthly EMI</b><span>{fmt(top.emi)}</span></div>
            <div className="pdf-metric"><b>ROI</b><span>{round2(top.roi)}x</span></div>
          </div>
          <h2 className="pdf-section-title">Recommended Pathways</h2>
          <table className="pdf-table">
            <thead><tr><th align="left">Career</th><th>Fit</th><th>Demand</th><th>EMI</th><th>ROI</th><th>Status</th></tr></thead>
            <tbody>
              {pathwayCareers.map(c => (
                <tr key={c.id}>
                  <td>{c.title}</td><td align="center">{c.fitPct}%</td><td align="center">{c.demandPct}%</td><td align="center">{fmt(c.emi)}</td><td align="center">{round2(c.roi)}x</td><td align="center">{c.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <h2 className="pdf-section-title">Family Alignment</h2>
          <div className="pdf-note"><b>PSCI Score:</b> {psciScore}/100. {conflict.detailed_narrative || conflict.resolution_hint || 'Conflict analysis pending.'}</div>
          <h2 className="pdf-section-title">Parent Constraints</h2>
          <div className="pdf-note">Budget: {fmt(parentProfile.budget_max_no_loan)} | Loan tolerance: {fmt(parentProfile.loan_tolerance)} | Mobility: {(parentProfile.location || '').replace(/_/g, ' ')} | Risk: {parentRisk}</div>
          <h2 className="pdf-section-title">Scholarships</h2>
          <ul className="pdf-list">{scholarships.slice(0, 5).map(s => <li key={s.name}><b>{s.name}</b>: {fmt(s.benefit_inr)}</li>)}</ul>
        </section>
        <div className="screen-only">
        {/* ── Header ──────────────────────────────────────────────────────────── */}
        <div className="border-b border-white/10 px-6 py-5 flex flex-wrap gap-4 items-center justify-between bg-[#0a1020]">
          <div>
            <p className="text-xs font-bold uppercase tracking-[0.3em] text-cyan-400">PRISM Decision Console</p>
            <h1 className="text-2xl font-black text-white mt-1">Career, Cost & Family Fit</h1>
          </div>
          <div className="flex gap-3 no-print flex-wrap">
            <select value={language} onChange={e => setLanguage(e.target.value)}
              className="px-3 py-2 bg-[#0a1020] border border-white/20 rounded-lg text-sm text-white focus:outline-none focus:border-indigo-500">
              <option value="English" className="bg-[#0a1020] text-white">English</option>
              <option value="Hindi" className="bg-[#0a1020] text-white">हिंदी</option>
              <option value="Tamil" className="bg-[#0a1020] text-white">தமிழ்</option>
              <option value="Telugu" className="bg-[#0a1020] text-white">తెలుగు</option>
            </select>
            <button onClick={downloadPDF}
              className="px-4 py-2 bg-white text-gray-900 font-bold rounded-lg text-sm hover:bg-gray-100">
              🖨️ Download PDF
            </button>
            <button onClick={() => navigate('/')}
              className="px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-sm hover:bg-white/20">
              ← Start Over
            </button>
          </div>
        </div>

        {/* ── Summary Bar ────────────────────────────────────────────────────── */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 p-6 border-b border-white/10">
          {[
            { label: 'Top Match', val: top.title || 'Pending', color: 'text-white' },
            { label: 'Best Value', val: bestValue.title || 'Pending', color: 'text-emerald-400' },
            { label: 'Avg EMI', val: fmt(avgEmi), color: 'text-white' },
            { label: 'PSCI Score', val: `${psciScore}/100 ${conflictSev}`, color: sevColor === '#10b981' ? 'text-emerald-400' : sevColor === '#f59e0b' ? 'text-yellow-400' : 'text-red-400' },
          ].map(({ label, val, color }) => (
            <div key={label} className="print-card bg-white/[0.04] border border-white/10 rounded-xl p-4">
              <p className="text-xs font-bold uppercase tracking-wider text-gray-400">{label}</p>
              <p className={`text-lg font-black mt-1 truncate ${color}`}>{val}</p>
            </div>
          ))}
        </div>

        <div className="print-grid grid grid-cols-1 lg:grid-cols-3 gap-6 p-6">
          <div className="print-main lg:col-span-2 space-y-6">

            {/* ── 3 Pathway Cards ────────────────────────────────────────────── */}
            <section className="print-card print-skip bg-white/[0.04] border border-white/10 rounded-2xl overflow-hidden">
              <div className="px-5 py-4 border-b border-white/10 flex justify-between items-center">
                <h2 className="font-bold text-lg">🎯 Your 3 Realistic Pathways</h2>
                <span className="text-xs font-mono bg-indigo-900/50 text-indigo-300 px-2 py-1 rounded">MAUT Ranked</span>
              </div>
              <div className="p-5 grid grid-cols-1 md:grid-cols-3 gap-4">
                {pathwayCareers.map((c, i) => (
                  <div key={c.id} className={`rounded-xl border p-4 relative ${i === 0 ? 'border-yellow-500/40 bg-yellow-500/5' : i === 1 ? 'border-indigo-500/30 bg-indigo-500/5' : 'border-white/10 bg-white/[0.02]'}`}>
                    <div className="text-2xl mb-1">{['🥇', '🥈', '🥉'][i]}</div>
                    <h3 className="font-bold text-white text-sm capitalize mb-3">{c.title}</h3>
                    <div className="space-y-1.5 text-xs">
                      <div className="flex justify-between">
                        <span className="text-gray-400">Career Fit</span>
                        <span className="font-bold text-indigo-300">{c.fitPct}%</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">ROI</span>
                        <span className="font-bold text-emerald-300">{round2(c.roi)}x</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">EMI</span>
                        <span className="font-bold text-white">{fmt(c.emi)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">Demand</span>
                        <span className="font-bold text-cyan-300">{c.demandPct}%</span>
                      </div>
                      <div className="pt-1.5 mt-1.5 border-t border-white/10">
                        <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${c.affordable ? 'bg-emerald-500/20 text-emerald-300' : 'bg-red-500/20 text-red-300'}`}>
                          {c.status}
                        </span>
                      </div>
                    </div>
                    {c.skills?.length > 0 && (
                      <div className="mt-3 pt-3 border-t border-white/10">
                        <p className="text-xs text-gray-500 mb-1">Skill Gap</p>
                        <p className="text-xs text-yellow-300">{c.skills.slice(0, 2).join(' + ')}</p>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </section>

            {/* ── Student–Parent Agreement ────────────────────────────────────── */}
            <section className="print-card print-skip bg-white/[0.04] border border-white/10 rounded-2xl overflow-hidden">
              <div className="px-5 py-4 border-b border-white/10">
                <h2 className="font-bold text-lg">❤️ Student–Parent Alignment</h2>
              </div>
              <div className="p-5">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-4 h-4 rounded-full" style={{ background: sevColor }} />
                  <span className="font-bold text-lg">{conflictSev} Conflict</span>
                  <span className="text-xs text-gray-400">(PSCI {psciScore}/100)</span>
                </div>
                <p className="text-sm text-gray-300 mb-5">{conflict.detailed_narrative || conflict.resolution_hint || 'Conflict analysis pending.'}</p>

                {compromise.length > 0 && (
                  <div>
                    <p className="text-xs font-bold uppercase tracking-wider text-gray-400 mb-2">🎯 PRISM Compromise Careers</p>
                    <div className="flex flex-wrap gap-2">
                      {compromise.map(id => (
                        <span key={id} className="px-3 py-1 bg-emerald-500/20 text-emerald-300 rounded-full text-xs font-bold border border-emerald-500/30">
                          {id.replace(/_/g, ' ')}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </section>

            {/* ── SWOT ───────────────────────────────────────────────────────── */}
            <section className="print-card bg-white/[0.04] border border-white/10 rounded-2xl overflow-hidden">
              <div className="px-5 py-4 border-b border-white/10 flex justify-between items-center">
                <h2 className="font-bold text-lg">📊 Psychometric SWOT Analysis</h2>
                <span className="text-xs font-mono bg-emerald-900/50 text-emerald-300 px-2 py-1 rounded">Engine Generated</span>
              </div>
              <div className="p-5 grid grid-cols-1 sm:grid-cols-2 gap-4">
                {[
                  { key: 'strengths', label: '💪 Strengths', bg: 'bg-emerald-500/10', border: 'border-emerald-500/30', text: 'text-emerald-300' },
                  { key: 'weaknesses', label: '⚠️ Weaknesses', bg: 'bg-yellow-500/10', border: 'border-yellow-500/30', text: 'text-yellow-300' },
                  { key: 'opportunities', label: '🚀 Opportunities', bg: 'bg-blue-500/10', border: 'border-blue-500/30', text: 'text-blue-300' },
                  { key: 'threats', label: '⚡ Threats', bg: 'bg-red-500/10', border: 'border-red-500/30', text: 'text-red-300' },
                ].map(({ key, label, bg, border, text }) => (
                  <div key={key} className={`${bg} border ${border} rounded-xl p-4`}>
                    <h3 className={`font-bold text-sm mb-3 ${text}`}>{label}</h3>
                    <ul className="space-y-1.5">
                      {(swot[key] || ['No data']).map((item, i) => (
                        <li key={i} className="text-xs text-gray-300 flex gap-2">
                          <span className={`${text} mt-0.5 shrink-0`}>•</span>
                          <span>{item}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            </section>

            {/* ── Radar Chart ────────────────────────────────────────────────── */}
            <section className="print-card bg-white/[0.04] border border-white/10 rounded-2xl overflow-hidden">
              <div className="px-5 py-4 border-b border-white/10 flex justify-between items-center">
                <h2 className="font-bold text-lg">🕸️ Psychometric Alignment (RIASEC)</h2>
                <span className="text-xs font-mono bg-indigo-900/50 text-indigo-300 px-2 py-1 rounded">Engine Validation</span>
              </div>
              <div className="h-80 p-4">
                <ResponsiveContainer width="100%" height="100%">
                  <RadarChart data={radarData}>
                    <PolarGrid stroke="rgba(255,255,255,0.1)" />
                    <PolarAngleAxis dataKey="subject" tick={{ fill: '#94a3b8', fontSize: 11, fontWeight: 600 }} />
                    <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
                    <Radar name="Your Profile" dataKey="student" stroke="#8b5cf6" fill="#8b5cf6" fillOpacity={0.4} />
                    <Radar name="Top Career Benchmark" dataKey="benchmark" stroke="#10b981" fill="#10b981" fillOpacity={0.3} />
                    <RechartsTooltip contentStyle={{ background: '#1e293b', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8 }} />
                    <Legend wrapperStyle={{ color: '#94a3b8', fontSize: 12 }} />
                  </RadarChart>
                </ResponsiveContainer>
              </div>
            </section>

            {/* ── Cost vs Value Quadrant ──────────────────────────────────────── */}
            <section className="print-card bg-white/[0.04] border border-white/10 rounded-2xl overflow-hidden">
              <div className="px-5 py-4 border-b border-white/10 flex justify-between items-center">
                <h2 className="font-bold text-lg">💹 Cost vs. Value Quadrant</h2>
                <span className="text-xs font-mono bg-blue-900/50 text-blue-300 px-2 py-1 rounded">Money vs College Ratio</span>
              </div>
              <div className="relative h-96 p-4">
                <div className="absolute top-6 left-8 text-xs font-bold text-emerald-400 bg-emerald-500/10 px-2 py-1 rounded border border-emerald-500/30 pointer-events-none z-10">🏛️ Golden Zone</div>
                <div className="absolute top-6 right-8 text-xs font-bold text-blue-400 bg-blue-500/10 px-2 py-1 rounded border border-blue-500/30 pointer-events-none z-10">💎 Premium Zone</div>
                <div className="absolute bottom-12 left-8 text-xs font-bold text-yellow-400 bg-yellow-500/10 px-2 py-1 rounded border border-yellow-500/30 pointer-events-none z-10">✅ Safe Zone</div>
                <div className="absolute bottom-12 right-8 text-xs font-bold text-red-400 bg-red-500/10 px-2 py-1 rounded border border-red-500/30 pointer-events-none z-10">⚠️ Danger Zone</div>
                <ResponsiveContainer width="100%" height="100%">
                  <ScatterChart margin={{ top: 30, right: 30, bottom: 20, left: 20 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                    <XAxis type="number" dataKey="emi" name="EMI" unit="₹" tick={{ fill: '#94a3b8', fontSize: 11 }} domain={['auto', 'auto']} />
                    <YAxis type="number" dataKey="roi" name="ROI" unit="x" tick={{ fill: '#94a3b8', fontSize: 11 }} domain={['auto', 'auto']} />
                    <ZAxis range={[120, 400]} />
                    <RechartsTooltip
                      contentStyle={{ background: '#1e293b', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8, color: 'white' }}
                      formatter={(v, name) => [name === 'EMI' ? fmt(v) : `${v.toFixed(2)}x`, name]}
                    />
                    <ReferenceLine x={avgEmi} stroke="rgba(255,255,255,0.2)" strokeDasharray="4 4" />
                    <ReferenceLine y={avgRoi} stroke="rgba(255,255,255,0.2)" strokeDasharray="4 4" />
                    <Scatter name="Careers" data={displayCareers} >
                      {displayCareers.map((c, i) => (
                        <Cell key={i} fill={zoneColor(c.emi, c.roi)} />
                      ))}
                    </Scatter>
                  </ScatterChart>
                </ResponsiveContainer>
              </div>
            </section>

            {/* ── Financial Check ─────────────────────────────────────────────── */}
            <section className="print-card bg-white/[0.04] border border-white/10 rounded-2xl overflow-hidden">
              <div className="px-5 py-4 border-b border-white/10">
                <h2 className="font-bold text-lg">💰 Financial Reality Check</h2>
              </div>
              <div className="p-5 grid grid-cols-3 gap-4">
                {[
                  { label: 'Monthly EMI', val: fmt(top.emi) },
                  { label: 'ROI Multiplier', val: `${round2(top.roi)}x` },
                  { label: 'Payback Period', val: `${isFinite(top.payback) ? Number(top.payback).toFixed(1) : 'N/A'} yrs` },
                ].map(({ label, val }) => (
                  <div key={label} className="bg-white/[0.04] border border-white/10 rounded-xl p-4 text-center">
                    <p className="text-xs text-gray-400 mb-1">{label}</p>
                    <p className="text-xl font-black text-white">{val}</p>
                  </div>
                ))}
              </div>
            </section>

            {/* ── Scholarships ───────────────────────────────────────────────── */}
            <section className="print-card bg-white/[0.04] border border-white/10 rounded-2xl overflow-hidden">
              <div className="px-5 py-4 border-b border-white/10 flex justify-between items-center">
                <h2 className="font-bold text-lg">🎓 Eligible Scholarships & Aid</h2>
                <span className="text-xs font-mono bg-yellow-900/50 text-yellow-300 px-2 py-1 rounded">Matched via PRISM</span>
              </div>
              <div className="p-5">
                {scholarships.length > 0 ? (
                  <div className="space-y-3">
                    {scholarships.map((s, i) => (
                      <div key={i} className="flex justify-between items-start p-4 bg-white/[0.03] border border-white/10 rounded-xl hover:border-emerald-500/40 transition-all">
                        <div className="flex-1 pr-4">
                          <h3 className="font-bold text-sm text-white">{s.name}</h3>
                          <p className="text-xs text-gray-400 mt-0.5">{s.provider || 'Government of India'}</p>
                          <p className="text-xs text-gray-300 mt-1">{(s.benefit_description || 'Financial assistance for eligible students').replace(/â‚¹/g, 'INR ')}</p>
                        </div>
                        <div className="shrink-0 px-3 py-1 bg-emerald-500/20 text-emerald-300 rounded-full text-sm font-bold border border-emerald-500/30">
                          {fmt(s.benefit_inr)}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-center text-gray-400 py-6">No scholarships matched. Try re-running with different mobility settings.</p>
                )}
              </div>
            </section>

            {/* ── Leaflet Map ─────────────────────────────────────────────────── */}
            <section className="print-card bg-white/[0.04] border border-white/10 rounded-2xl overflow-hidden no-print">
              <div className="px-5 py-4 border-b border-white/10 flex justify-between items-center">
                <h2 className="font-bold text-lg">📍 Hyper-Local Institutions</h2>
                <span className="text-xs font-mono bg-emerald-900/50 text-emerald-300 px-2 py-1 rounded">OpenStreetMap Live</span>
              </div>
              <div className="p-5">
                <p className="text-sm text-gray-400 mb-3">
                  Searching <strong className="text-indigo-300 capitalize">{mapTerm}</strong> in <strong>{locationLabel}</strong>.
                  <span className="text-xs ml-2 text-gray-500">🟣 You · 🟢 Colleges · 🟡 Demand Hubs</span>
                </p>
                <a href={mapOpenUrl} target="_blank" rel="noreferrer" className="inline-flex mb-3 px-3 py-2 bg-emerald-500/20 text-emerald-300 rounded-lg text-xs font-bold border border-emerald-500/30">
                  Open nearby colleges in Google Maps
                </a>
                <iframe
                  title="PRISM institution map"
                  src={mapEmbedUrl}
                  className="w-full h-80 rounded-xl overflow-hidden border border-white/10 bg-gray-900"
                  loading="lazy"
                />
              </div>
            </section>

          </div>

          {/* ── Sidebar ──────────────────────────────────────────────────────── */}
          <div className="space-y-6 no-print">

            {/* Parent Details Card */}
            {(parentProfile.budget_max_no_loan || parentProfile.location) && (
              <section className="print-card bg-white/[0.04] border border-white/10 rounded-2xl overflow-hidden">
                <div className="px-5 py-4 border-b border-white/10">
                  <h2 className="font-bold text-sm">👨‍👩‍👧 Parent Constraints</h2>
                </div>
                <div className="p-4 space-y-2 text-xs">
                  <div className="flex justify-between">
                    <span className="text-gray-400">Max Budget</span>
                    <span className="font-bold text-white">{fmt(parentProfile.budget_max_no_loan)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Loan Tolerance</span>
                    <span className="font-bold text-white">{fmt(parentProfile.loan_tolerance)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Mobility</span>
                    <span className="font-bold text-white capitalize">{(parentProfile.location || '').replace(/_/g, ' ')}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Risk Level</span>
                    <span className="font-bold text-white">{parentRisk}</span>
                  </div>
                </div>
              </section>
            )}

            {/* Chat */}
            <section className="bg-[#0a1020] border border-indigo-500/30 rounded-2xl overflow-hidden flex flex-col no-print" style={{ height: 520 }}>
              <div className="bg-indigo-600 px-4 py-3 flex items-center justify-between">
                <span className="font-bold text-sm">🤖 PRISM Counselor</span>
                <span className="text-xs text-indigo-200">{language}</span>
              </div>
              <div className="flex-1 p-4 overflow-y-auto space-y-3 bg-[#070b14]">
                {chatMessages.map((m, i) => (
                  <div key={i} className={`flex ${m.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
                    <div className={`max-w-[85%] rounded-xl px-4 py-2.5 text-sm whitespace-pre-wrap ${m.sender === 'user' ? 'bg-indigo-600 text-white rounded-br-none' : 'bg-white/10 text-gray-200 border border-white/10 rounded-bl-none'}`}>
                      {m.text}
                    </div>
                  </div>
                ))}
                {chatLoading && (
                  <div className="flex gap-1.5 pl-1">
                    {[0, 1, 2].map(i => <div key={i} className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: `${i * 0.2}s` }} />)}
                  </div>
                )}
              </div>
              <div className="p-3 border-t border-white/10 bg-[#0a1020] flex gap-2">
                <input
                  value={chatInput}
                  onChange={e => setChatInput(e.target.value)}
                  onKeyDown={e => e.key === 'Enter' && sendChat()}
                  placeholder="Ask about your results..."
                  className="flex-1 bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-indigo-500"
                />
                <button onClick={sendChat} disabled={chatLoading || !chatInput.trim()}
                  className="px-4 py-2 bg-indigo-600 rounded-lg text-sm font-bold hover:bg-indigo-700 disabled:opacity-50">
                  Send
                </button>
              </div>
            </section>

          </div>
        </div>
        </div>
      </div>
    </>
  );
}
