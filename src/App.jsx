import { useState, useEffect } from 'react';
import { Activity, Users, FileText, Zap, ChevronRight, BarChart3, TrendingUp, Filter, AlertTriangle } from 'lucide-react';
import { LineChart, Line, Tooltip, ResponsiveContainer, YAxis, PieChart, Pie, Cell, Legend } from 'recharts';

const RechartsSparkline = ({ data }) => {
  if (!data || data.length < 2) return <div style={{width: '120px', height: '40px'}}></div>;
  
  const chartData = data;
  const values = data.map(d => d.value);
  const min = Math.min(...values);
  const max = Math.max(...values);
  const diff = max - min || 1;
  const domain = [Math.max(0, min - diff * 0.1), max + diff * 0.1];

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const p = payload[0].payload;
      const dateStr = p.date === 'Now' ? 'Now' : new Date(p.date).toLocaleDateString();
      return (
        <div style={{ background: 'rgba(15, 23, 42, 0.95)', border: '1px solid rgba(59, 130, 246, 0.3)', padding: '6px 10px', borderRadius: '4px', fontSize: '0.8rem', color: '#f8fafc', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.5)' }}>
          <div style={{ color: 'var(--text-muted)', marginBottom: '3px', fontSize: '0.7rem', textTransform: 'uppercase' }}>{dateStr}</div>
          <div><strong>{p.value.toLocaleString()}</strong> sig.</div>
        </div>
      );
    }
    return null;
  };

  return (
    <div style={{ width: '120px', height: '40px' }}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData}>
          <YAxis domain={domain} hide />
          <Tooltip 
            content={<CustomTooltip />} 
            cursor={{ stroke: 'rgba(255,255,255,0.1)', strokeWidth: 1 }} 
            isAnimationActive={false} 
            offset={20}
            position={{ y: -35 }}
            allowEscapeViewBox={{ x: true, y: true }}
            wrapperStyle={{ zIndex: 100 }}
          />
          <Line type="monotone" dataKey="value" stroke="#3b82f6" strokeWidth={2.5} dot={false} activeDot={{ r: 4, fill: '#60a5fa', stroke: '#fff', strokeWidth: 1 }} isAnimationActive={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

function App() {
  const [lang, setLang] = useState('en');
  const [kpis, setKpis] = useState(null);
  const [trending, setTrending] = useState([]);
  const [phases, setPhases] = useState([]);
  const [summary, setSummary] = useState(null);
  const [stalled, setStalled] = useState([]);
  const [loading, setLoading] = useState(true);

  // Simple translations for MVP
  const t = {
    en: {
      title: "Estonian Civic Initiatives",
      subtitle: "Monitoring Rahvaalgatus Momentum & Lifecycle",
      overview: "Overview",
      total_initiatives: "Total Initiatives",
      active_initiatives: "Active Initiatives",
      total_signatures: "Total Signatures",
      momentum: "Trending Initiatives",
      signatures: "signatures",
      view_timeline: "View Timeline",
      phase_sign: "Signing",
      phase_parliament: "Parliament",
      phase_processing: "Processing",
      phase_completed: "Completed",
      phase_archived: "Archived",
      phase_done: "Done",
      phase_edit: "Draft/Edit",
      phase_government: "Government",
      phase_rejected: "Rejected",
      phase_other: "Other",
      summary_title: "Recent Platform Activity",
      new_initiatives: "New initiatives in the last 30 days",
      latest_activity: "Latest platform activity",
      on: "on",
      velocity: "sig./day",
      growth: "7d growth",
      process: "Process & Funnel",
      funnel_title: "Phase Funnel",
      stalled_title: "Stalled Initiatives",
      idle_days: "days idle"
    },
    et: {
      title: "Eesti Rahvaalgatused",
      subtitle: "Rahvaalgatuste hoo ja elutsükli jälgimine",
      overview: "Ülevaade",
      total_initiatives: "Algatusi Kokku",
      active_initiatives: "Aktiivsed Algatused",
      total_signatures: "Allkirju Kokku",
      momentum: "Kuumad Algatused",
      signatures: "allkirja",
      view_timeline: "Vaata Ajajoont",
      phase_sign: "Allkirjastamine",
      phase_parliament: "Parlament",
      phase_processing: "Menetluses",
      phase_completed: "Lõpetatud",
      phase_archived: "Arhiveeritud",
      phase_done: "Tehtud",
      phase_edit: "Koostamisel",
      phase_government: "Valitsus",
      phase_rejected: "Tagasi lükatud",
      phase_other: "Muu",
      summary_title: "Hiljutine Aktiivsus",
      new_initiatives: "Uusi algatusi viimase 30 päeva jooksul",
      latest_activity: "Viimane tegevus platvormil",
      on: "kuupäeval",
      velocity: "allkirja/päev",
      growth: "7p kasv",
      process: "Protsess ja Lehter",
      funnel_title: "Faaside Lehter",
      stalled_title: "Seisvad Algatused",
      idle_days: "päeva ootel"
    }
  };

  useEffect(() => {
    async function fetchData() {
      try {
        const [kpiRes, trendRes, sumRes, stalledRes] = await Promise.all([
          fetch('/api_data/kpis.json'),
          fetch('/api_data/trending.json'),
          fetch('/api_data/summary.json'),
          fetch('/api_data/stalled.json')
        ]);
        
        const kpiData = await kpiRes.json();
        const trendData = await trendRes.json();
        const sumData = await sumRes.json();
        const stalledData = await stalledRes.json();
        
        setKpis(kpiData);
        setTrending(trendData);
        setSummary(sumData);
        setStalled(stalledData);
      } catch (err) {
        console.error("Error fetching data:", err);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="container">
        <div className="loading">Loading Civic Data...</div>
      </div>
    );
  }

  const activeT = t[lang];

  const phaseColors = {
    'sign': '#10b981', // green
    'parliament': '#3b82f6', // blue
    'processing': '#f59e0b', // yellow 
    'completed': '#8b5cf6', // purple
    'archived': '#64748b', // gray
    'rejected': '#ef4444', // red
    'done': '#8b5cf6',     // purple (same as completed)
    'edit': '#94a3b8',     // light gray (drafting)
    'government': '#eab308'// yellow
  };

  const getPhaseName = (slug) => activeT[`phase_${slug}`] || activeT.phase_other || slug;

  const getPhaseCount = (phase) => {
    const p = phases.find(p => p.phase === phase);
    return p ? p.count : 0;
  };
  
  const funnelData = [
    { id: 'total', label: activeT.total_initiatives, count: kpis?.total_initiatives || 0, color: '#3b82f6' },
    { id: 'sign', label: getPhaseName('sign'), count: getPhaseCount('sign'), color: '#10b981' },
    { id: 'parliament', label: getPhaseName('parliament'), count: getPhaseCount('parliament'), color: '#8b5cf6' },
    { id: 'government', label: getPhaseName('government'), count: getPhaseCount('government'), color: '#eab308' },
    { id: 'done', label: getPhaseName('done'), count: getPhaseCount('done'), color: '#64748b' }
  ];
  const maxFunnel = funnelData[0].count || 1;

  return (
    <div className="container">
      <header>
        <h1>{activeT.title}</h1>
        <p>{activeT.subtitle}</p>
        {summary?.last_update && (
           <p style={{fontSize: '0.85rem', color: 'var(--text-muted, #94a3b8)', margin: '0.5rem 0 1rem 0'}}>
             {lang === 'en' ? 'Last Updated:' : 'Viimati uuendatud:'} {new Date(summary.last_update).toLocaleString()}
           </p>
        )}
        <div className="lang-switch">
          <button className={lang === 'en' ? 'active' : ''} onClick={() => setLang('en')}>EN</button>
          <button className={lang === 'et' ? 'active' : ''} onClick={() => setLang('et')}>ET</button>
        </div>
      </header>

      <main>
        {/* BLOCK 1: OVERVIEW */}
        <div className="dashboard-grid">
          <div className="glass-panel">
            <div className="kpi-title"><FileText size={16} style={{display:'inline', verticalAlign:'bottom', marginRight:4}}/> {activeT.total_initiatives}</div>
            <div className="kpi-value">{kpis?.total_initiatives || '0'}</div>
          </div>
          <div className="glass-panel">
            <div className="kpi-title"><Activity size={16} style={{display:'inline', verticalAlign:'bottom', marginRight:4}}/> {activeT.active_initiatives}</div>
            <div className="kpi-value" style={{color: '#60a5fa'}}>{kpis?.active_initiatives || '0'}</div>
          </div>
          <div className="glass-panel">
            <div className="kpi-title"><Users size={16} style={{display:'inline', verticalAlign:'bottom', marginRight:4}}/> {activeT.total_signatures}</div>
            <div className="kpi-value">{kpis?.total_signatures ? kpis.total_signatures.toLocaleString() : '0'}</div>
          </div>
        </div>

        {/* BLOCK 1.5: PHASE DIST & SUMMARY */}
        <div className="dashboard-grid" style={{gridTemplateColumns: '2fr 1fr'}}>
          <div className="glass-panel">
            <h2 className="section-title"><BarChart3 size={20} color="#60a5fa"/> Phase Distribution</h2>
            <div className="phase-bar-container">
              <div className="phase-bar">
                {phases.map(p => {
                  const width = `${(p.count / Math.max(1, kpis?.total_initiatives || 1)) * 100}%`;
                  const color = phaseColors[p.phase] || '#cbd5e1';
                  return <div key={p.phase} className="phase-segment" style={{width, backgroundColor: color}} title={`${getPhaseName(p.phase)}: ${p.count}`} />
                })}
              </div>
              <div className="phase-legend">
                {phases.map(p => (
                  <div key={p.phase} className="legend-item">
                    <span className="legend-dot" style={{backgroundColor: phaseColors[p.phase] || '#cbd5e1'}}></span>
                    {getPhaseName(p.phase)} ({p.count})
                  </div>
                ))}
              </div>
            </div>
          </div>
          
          <div className="glass-panel">
            <div className="summary-box">
              <h3 style={{marginBottom: '1rem', color:'#fff', fontSize: '1.1rem'}}>{activeT.summary_title}</h3>
              <p><strong>{summary?.new_in_30_days || 0}</strong> {activeT.new_initiatives.toLowerCase()}</p>
              {summary?.latest_event && (
                <div style={{marginTop: '1rem'}}>
                  <p style={{color: '#60a5fa', fontSize:'0.85rem', marginBottom: '0.2rem'}}>{activeT.latest_activity.toUpperCase()}</p>
                  <p><strong>{summary?.latest_event?.title}</strong></p>
                  <p style={{fontSize:'0.85rem', marginTop: '0.3rem'}}>{summary?.latest_event?.actor} {activeT.on} {new Date(summary?.latest_event?.date).toLocaleDateString()}</p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* BLOCK 2: MOMENTUM */}
        <div className="dashboard-grid" style={{gridTemplateColumns: '1fr'}}>
          <div className="glass-panel">
            <h2 className="section-title"><TrendingUp size={20} color="#fbbf24"/> {activeT.momentum}</h2>
            <div>
              {trending.map((item, idx) => (
                <div className="list-item" key={item.id} style={{display:'flex', alignItems: 'center'}}>
                  <a href={item.url} target="_blank" rel="noopener noreferrer" className="trending-link" style={{display:'flex', flex: 1, textDecoration:'none', color:'inherit', alignItems: 'center'}}>
                    <div style={{marginRight: '1.2rem', color: 'var(--text-muted)', fontWeight: 600, fontSize: '1.2rem', minWidth: '20px'}}>
                      {idx + 1}
                    </div>
                    <div className="item-info" style={{ flex: 1, minWidth: 0 }}>
                      <h4 style={{fontSize: '1.1rem', maxWidth: '100%', whiteSpace: 'normal', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden'}}>{item.title}</h4>
                      <span style={{color: '#fff', fontWeight: 500, fontSize: '0.95rem'}}>{item.signatures_count.toLocaleString()}</span> {activeT.signatures}
                      <span className="badge badge-sign" style={{marginLeft: '0.8rem', fontSize: '0.7rem', padding: '0.15rem 0.5rem'}}>{activeT.phase_sign}</span>
                      {item.velocity >= 0 && (
                        <span style={{marginLeft: '0.8rem', color: '#10b981', fontSize: '0.85rem', fontWeight: 500, background: 'rgba(16, 185, 129, 0.1)', padding:'0.2rem 0.6rem', borderRadius:'999px'}} title="Average daily growth over 7 days">
                          +{item.velocity} {activeT.velocity}
                        </span>
                      )}
                    </div>
                    <div style={{ color: 'var(--text-muted)', opacity: 0.5, margin: '0 1rem', display: 'flex', alignItems: 'center' }}>
                      <ChevronRight size={20} />
                    </div>
                  </a>
                  <div style={{display:'flex', alignItems:'center'}}>
                    <RechartsSparkline data={item.history_array} />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* BLOCK 3: PROCESS */}
        <div className="dashboard-grid" style={{gridTemplateColumns: '1fr 1fr'}}>
          
          <div className="glass-panel" style={{ display: 'flex', flexDirection: 'column' }}>
            <h2 className="section-title"><Activity size={20} color="#8b5cf6"/> Fate of Initiatives</h2>
            
            {/* Idea 1: Cards */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1.5rem' }}>
              <div style={{ background: 'rgba(255,255,255,0.03)', padding: '0.8rem', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.05)' }}>
                <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '0.2rem' }}>Active Gathering</div>
                <div style={{ fontSize: '1.3rem', fontWeight: 600, color: '#10b981' }}>{getPhaseCount('sign').toLocaleString()}</div>
              </div>
              <div style={{ background: 'rgba(255,255,255,0.03)', padding: '0.8rem', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.05)' }}>
                <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '0.2rem' }}>Under Review</div>
                <div style={{ fontSize: '1.3rem', fontWeight: 600, color: '#f59e0b' }}>{(getPhaseCount('parliament') + getPhaseCount('government')).toLocaleString()}</div>
              </div>
              <div style={{ background: 'rgba(255,255,255,0.03)', padding: '0.8rem', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.05)' }}>
                <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '0.2rem' }}>Successfully Done</div>
                <div style={{ fontSize: '1.3rem', fontWeight: 600, color: '#8b5cf6' }}>{getPhaseCount('done').toLocaleString()}</div>
              </div>
              <div style={{ background: 'rgba(255,255,255,0.03)', padding: '0.8rem', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.05)' }}>
                <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '0.2rem' }}>Total Initiatives</div>
                <div style={{ fontSize: '1.3rem', fontWeight: 600, color: '#3b82f6' }}>{kpis?.total_initiatives?.toLocaleString() || 0}</div>
              </div>
            </div>

            {/* Idea 2: Donut Chart */}
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', marginTop: '1rem', marginBottom: '1.5rem', background: 'rgba(255,255,255,0.02)', borderRadius: '8px', padding: '1rem' }}>
               <h3 style={{ fontSize: '1rem', color: '#fff', marginBottom: '0.5rem', width: '100%', textAlign: 'center' }}>Overall Success Rate</h3>
               <div style={{ width: '100%', height: '220px' }}>
                 <ResponsiveContainer width="100%" height="100%">
                   <PieChart>
                     <Pie
                       data={[
                         { name: 'Done', value: getPhaseCount('done'), color: '#8b5cf6' },
                         { name: 'Under Review', value: getPhaseCount('parliament') + getPhaseCount('government'), color: '#f59e0b' },
                         { name: 'Active', value: getPhaseCount('sign'), color: '#10b981' },
                         { name: 'Other/Failed', value: (kpis?.total_initiatives || 0) - (getPhaseCount('done') + getPhaseCount('parliament') + getPhaseCount('government') + getPhaseCount('sign')), color: '#475569' }
                       ]}
                       cx="50%"
                       cy="45%"
                       innerRadius={45}
                       outerRadius={65}
                       paddingAngle={5}
                       dataKey="value"
                       stroke="none"
                     >
                       {[
                         { name: 'Done', value: getPhaseCount('done'), color: '#8b5cf6' },
                         { name: 'Under Review', value: getPhaseCount('parliament') + getPhaseCount('government'), color: '#f59e0b' },
                         { name: 'Active', value: getPhaseCount('sign'), color: '#10b981' },
                         { name: 'Other/Failed', value: (kpis?.total_initiatives || 0) - (getPhaseCount('done') + getPhaseCount('parliament') + getPhaseCount('government') + getPhaseCount('sign')), color: '#475569' }
                       ].map((entry, index) => (
                         <Cell key={`cell-${index}`} fill={entry.color} />
                       ))}
                     </Pie>
                     <Tooltip 
                       contentStyle={{ background: 'rgba(15, 23, 42, 0.95)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }}
                       itemStyle={{ color: '#fff' }}
                       formatter={(value, name) => [`${value} init.`, name]}
                     />
                     <Legend verticalAlign="bottom" height={36} iconType="circle" wrapperStyle={{ fontSize: '0.75rem', paddingTop: '10px' }} />
                   </PieChart>
                 </ResponsiveContainer>
               </div>
            </div>

            {/* Idea 3: True Funnel */}
            <h3 style={{ fontSize: '1rem', color: '#fff', marginBottom: '1rem' }}>True Success Funnel</h3>
            <div className="funnel-container" style={{ alignItems: 'center', width: '100%', gap: '0.3rem' }}>
               <div className="funnel-row" style={{ width: '100%', background: 'rgba(59, 130, 246, 0.05)', border: '1px solid #3b82f640', justifyContent: 'center', padding: '0.5rem', gap: '1rem' }}>
                  <span style={{ color: '#3b82f6', fontSize: '0.9rem' }}>Total Created</span>
                  <span style={{ fontSize: '1.1rem' }}>{(kpis?.total_initiatives || 0).toLocaleString()}</span>
               </div>
               
               <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  ↓ {kpis?.total_initiatives ? Math.round(((kpis?.threshold_passed || 0) / kpis.total_initiatives) * 100) : 0}% passed 1000 sigs
               </div>
               
               <div className="funnel-row" style={{ width: '75%', background: 'rgba(245, 158, 11, 0.05)', border: '1px solid #f59e0b40', justifyContent: 'center', padding: '0.5rem', gap: '1rem' }}>
                  <span style={{ color: '#f59e0b', fontSize: '0.9rem' }}>Threshold Passed</span>
                  <span style={{ fontSize: '1.1rem' }}>{(kpis?.threshold_passed || 0).toLocaleString()}</span>
               </div>

               <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  ↓ {kpis?.threshold_passed ? Math.round((getPhaseCount('done') / kpis.threshold_passed) * 100) : 0}% implemented
               </div>

               <div className="funnel-row" style={{ width: '50%', background: 'rgba(139, 92, 246, 0.05)', border: '1px solid #8b5cf640', justifyContent: 'center', padding: '0.5rem', gap: '1rem' }}>
                  <span style={{ color: '#8b5cf6', fontSize: '0.9rem' }}>Successfully Done</span>
                  <span style={{ fontSize: '1.1rem' }}>{getPhaseCount('done').toLocaleString()}</span>
               </div>
            </div>
          </div>
          
          <div className="glass-panel">
            <h2 className="section-title"><AlertTriangle size={20} color="#fca5a5"/> {activeT.stalled_title}</h2>
            <div>
              {stalled.map(item => (
                <a href={item.url} target="_blank" rel="noopener noreferrer" className="list-item" key={item.id} style={{display:'flex', textDecoration:'none', color:'inherit'}}>
                  <div className="item-info" style={{flex: 1}}>
                    <h4 style={{fontSize: '1.05rem', whiteSpace: 'normal', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden'}}>{item.title}</h4>
                    <span style={{color: phaseColors[item.phase] || '#cbd5e1', fontSize: '0.8rem', textTransform: 'uppercase', letterSpacing: '0.5px'}}>{getPhaseName(item.phase)}</span>
                  </div>
                  <div>
                    <span className="stalled-badge">{item.days_stalled} {activeT.idle_days}</span>
                    <button style={{background:'transparent', border:'none', color:'var(--accent)', cursor:'pointer', marginLeft:'0.5rem'}}>
                      <ChevronRight size={20}/>
                    </button>
                  </div>
                </a>
              ))}
              {stalled.length === 0 && <p style={{color: 'var(--text-muted)'}}>No stalled initiatives.</p>}
            </div>
          </div>

        </div>

      </main>
    </div>
  );
}

export default App;
