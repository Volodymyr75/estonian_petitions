import { useState, useEffect } from 'react';
import { Activity, Users, FileText, Zap, ChevronRight, BarChart3 } from 'lucide-react';

function App() {
  const [lang, setLang] = useState('en');
  const [kpis, setKpis] = useState(null);
  const [trending, setTrending] = useState([]);
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
      phase_sign: "Signing"
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
      phase_sign: "Allkirjastamine"
    }
  };

  useEffect(() => {
    async function fetchData() {
      try {
        const [kpiRes, trendRes] = await Promise.all([
          fetch('/api/kpis'),
          fetch('/api/trending?limit=5')
        ]);
        
        const kpiData = await kpiRes.json();
        const trendData = await trendRes.json();
        
        setKpis(kpiData);
        setTrending(trendData);
        setLoading(false);
      } catch (err) {
        console.error("Error fetching data:", err);
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

  return (
    <div className="container">
      <header>
        <h1>{activeT.title}</h1>
        <p>{activeT.subtitle}</p>
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

        {/* BLOCK 2: MOMENTUM */}
        <div className="dashboard-grid" style={{gridTemplateColumns: '1fr'}}>
          <div className="glass-panel">
            <h2 className="section-title"><Zap size={20} color="#fbbf24"/> {activeT.momentum}</h2>
            <div>
              {trending.map(item => (
                <div className="list-item" key={item.id}>
                  <div className="item-info">
                    <h4>{item.title}</h4>
                    <span>{item.signatures_count.toLocaleString()} {activeT.signatures}</span>
                  </div>
                  <div>
                    <span className="badge badge-sign">{activeT.phase_sign}</span>
                    <button style={{background:'transparent', border:'none', color:'var(--accent)', cursor:'pointer', marginLeft:'1rem'}}>
                      <ChevronRight size={20}/>
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

      </main>
    </div>
  );
}

export default App;
