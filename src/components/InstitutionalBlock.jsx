import { useState, useEffect } from 'react';
import { Landmark, Vote, Calendar, Clock, ChevronRight, Search, FileCheck, CheckCircle2, AlertCircle, FileText } from 'lucide-react';

export default function InstitutionalBlock({ lang }) {
  const [data, setData] = useState(null);
  const [details, setDetails] = useState({});
  const [loading, setLoading] = useState(true);
  const [selectedInitId, setSelectedInitId] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [expandedVotingId, setExpandedVotingId] = useState(null);

  // Translations
  const t = {
    en: {
      title: "Parliament & Institutional Layer",
      subtitle: "Tracking civic initiatives in the Estonian Parliament (Riigikogu)",
      total_petitions: "Petitions Received",
      completed: "Completed Proceedings",
      with_draft: "Petitions with Draft Bills",
      status: "Status",
      filter_all: "All Statuses",
      filter_registered: "Registered",
      filter_committee: "In Committee",
      filter_completed: "Completed",
      search_placeholder: "Search petitions...",
      select_placeholder: "Select an initiative from the list to inspect its parliamentary timeline, draft bills, and voting results.",
      submitted_on: "Submitted on",
      committee: "Committee",
      outcome: "Outcome",
      timeline: "Parliamentary Progress",
      draft_info: "Associated Draft Bill (Eelnõu)",
      draft_status: "Draft Status",
      votings_title: "Plenary Votings",
      in_favor: "Yes",
      against: "No",
      neutral: "Abstained / Neutral",
      present: "Present",
      absent: "Absent",
      faction_breakdown: "Faction Vote Breakdown",
      no_votings: "No plenary votings recorded for this draft yet.",
      outcome_not_resolved: "In progress",
      mapped_title: "Petitions in Parliament"
    },
    et: {
      title: "Parlamendi ja institutsionaalne tasand",
      subtitle: "Rahvaalgatuste menetlemine Eesti Vabariigi Riigikogus",
      total_petitions: "Riigikogule esitatud pöördumised",
      completed: "Menetlus lõpetatud",
      with_draft: "Eelnõuga algatused",
      status: "Staatus",
      filter_all: "Kõik staatused",
      filter_registered: "Registreeritud",
      filter_committee: "Komisjonis",
      filter_completed: "Lõpetatud",
      search_placeholder: "Otsi pöördumist...",
      select_placeholder: "Vali nimekirjast algatus, et näha selle parlamendi ajajoont, seaduseelnõu detaile ja hääletustulemusi.",
      submitted_on: "Esitatud",
      committee: "Komisjon",
      outcome: "Tulemus",
      timeline: "Menetluskäik parlamendis",
      draft_info: "Seotud seaduseelnõu",
      draft_status: "Eelnõu staatus",
      votings_title: "Täiskogu hääletused",
      in_favor: "Poolt",
      against: "Vastu",
      neutral: "Erapooletu / Puudub",
      present: "Kohal",
      absent: "Puudub",
      faction_breakdown: "Hääled fraktsioonide kaupa",
      no_votings: "Selle eelnõu kohta pole veel täiskogu hääletusi registreeritud.",
      outcome_not_resolved: "Menetluses",
      mapped_title: "Riigikokku jõudnud algatused"
    }
  };

  const activeT = t[lang];

  useEffect(() => {
    async function fetchData() {
      try {
        const [instRes, detailsRes] = await Promise.all([
          fetch('/api_data/institutions.json'),
          fetch('/api_data/institutions_details.json')
        ]);
        const instData = await instRes.json();
        const detailsData = await detailsRes.json();

        setData(instData);
        setDetails(detailsData);
        
        // Select first petition by default if list is not empty
        if (instData.petitions && instData.petitions.length > 0) {
          setSelectedInitId(instData.petitions[0].initiative_id);
        }
      } catch (err) {
        console.error("Error loading institutions data:", err);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  if (loading) {
    return <div className="loading">Loading Parliament Data...</div>;
  }

  if (!data) return null;

  const { overview, petitions } = data;

  // Filter logic
  const filteredPetitions = petitions.filter(p => {
    const matchesSearch = p.title.toLowerCase().includes(searchTerm.toLowerCase()) || 
                          (p.reference && p.reference.toLowerCase().includes(searchTerm.toLowerCase()));
    
    if (statusFilter === 'ALL') return matchesSearch;
    if (statusFilter === 'REGISTERED') return matchesSearch && p.current_status === 'Registreeritud';
    if (statusFilter === 'COMMITTEE') return matchesSearch && p.current_status === 'Arutelu komisjonis';
    if (statusFilter === 'COMPLETED') return matchesSearch && p.current_status === 'Menetlus lõpetatud';
    return matchesSearch;
  });

  const selectedDetails = selectedInitId ? details[selectedInitId] : null;

  const getStatusBadgeClass = (status) => {
    if (status === 'Menetlus lõpetatud') return 'badge badge-completed-parl';
    if (status === 'Arutelu komisjonis' || status === 'Arutelu täiskogul') return 'badge badge-warning';
    return 'badge badge-info';
  };

  return (
    <div style={{ marginTop: '2rem', marginBottom: '2rem' }}>
      {/* SECTION HEADER */}
      <div className="section-title" style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', borderBottom: '1px solid rgba(255,255,255,0.05)', paddingBottom: '0.75rem', marginBottom: '1.5rem' }}>
        <Landmark size={24} color="#60a5fa" />
        <div>
          <h2 style={{ fontSize: '1.4rem', fontWeight: 600, color: '#fff', margin: 0 }}>{activeT.title}</h2>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: 400, marginTop: '2px' }}>{activeT.subtitle}</p>
        </div>
      </div>

      {/* KPI GRID */}
      <div className="dashboard-grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', marginBottom: '1.5rem' }}>
        <div className="glass-panel" style={{ padding: '1.2rem' }}>
          <div className="kpi-title"><Landmark size={15} style={{ display: 'inline', verticalAlign: 'bottom', marginRight: 5 }} /> {activeT.total_petitions}</div>
          <div className="kpi-value" style={{ fontSize: '2.4rem' }}>{overview.total_petitions}</div>
        </div>
        <div className="glass-panel" style={{ padding: '1.2rem' }}>
          <div className="kpi-title"><CheckCircle2 size={15} style={{ display: 'inline', verticalAlign: 'bottom', marginRight: 5 }} /> {activeT.completed}</div>
          <div className="kpi-value" style={{ fontSize: '2.4rem', color: '#c084fc' }}>{overview.completed_petitions}</div>
        </div>
        <div className="glass-panel" style={{ padding: '1.2rem' }}>
          <div className="kpi-title"><FileCheck size={15} style={{ display: 'inline', verticalAlign: 'bottom', marginRight: 5 }} /> {activeT.with_draft}</div>
          <div className="kpi-value" style={{ fontSize: '2.4rem', color: '#60a5fa' }}>{overview.petitions_with_drafts}</div>
        </div>
      </div>

      {/* DUAL-COLUMN WORKSPACE */}
      <div className="dashboard-grid institutions-layout" style={{ alignItems: 'stretch' }}>
        
        {/* LEFT COLUMN: LIST & SEARCH */}
        <div className="glass-panel" style={{ display: 'flex', flexDirection: 'column', maxHeight: '650px', padding: '1.2rem', minWidth: 0 }}>
          <h3 style={{ fontSize: '1.05rem', color: '#fff', marginBottom: '0.8rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <FileText size={18} color="#60a5fa" />
            {activeT.mapped_title} ({filteredPetitions.length})
          </h3>
          
          {/* Search bar */}
          <div style={{ position: 'relative', marginBottom: '0.8rem' }}>
            <Search size={16} style={{ position: 'absolute', left: '10px', top: '10px', color: 'var(--text-muted)' }} />
            <input 
              type="text"
              placeholder={activeT.search_placeholder}
              value={searchTerm}
              onChange={e => setSearchTerm(e.target.value)}
              style={{
                width: '100%',
                padding: '0.55rem 0.8rem 0.55rem 2.2rem',
                borderRadius: '8px',
                background: 'rgba(255, 255, 255, 0.03)',
                border: '1px solid rgba(255,255,255,0.08)',
                color: '#fff',
                fontSize: '0.9rem',
                outline: 'none'
              }}
            />
          </div>

          {/* Quick status filters */}
          <div style={{ display: 'flex', gap: '0.4rem', marginBottom: '1rem', flexWrap: 'wrap' }}>
            <button 
              onClick={() => setStatusFilter('ALL')} 
              style={{ padding: '0.25rem 0.6rem', borderRadius: '6px', fontSize: '0.75rem', fontWeight: 500, cursor: 'pointer', background: statusFilter === 'ALL' ? 'rgba(59, 130, 246, 0.2)' : 'transparent', border: '1px solid rgba(59, 130, 246, 0.3)', color: statusFilter === 'ALL' ? '#93c5fd' : 'var(--text-muted)' }}
            >
              {activeT.filter_all}
            </button>
            <button 
              onClick={() => setStatusFilter('REGISTERED')} 
              style={{ padding: '0.25rem 0.6rem', borderRadius: '6px', fontSize: '0.75rem', fontWeight: 500, cursor: 'pointer', background: statusFilter === 'REGISTERED' ? 'rgba(59, 130, 246, 0.2)' : 'transparent', border: '1px solid rgba(59, 130, 246, 0.3)', color: statusFilter === 'REGISTERED' ? '#93c5fd' : 'var(--text-muted)' }}
            >
              {activeT.filter_registered}
            </button>
            <button 
              onClick={() => setStatusFilter('COMMITTEE')} 
              style={{ padding: '0.25rem 0.6rem', borderRadius: '6px', fontSize: '0.75rem', fontWeight: 500, cursor: 'pointer', background: statusFilter === 'COMMITTEE' ? 'rgba(59, 130, 246, 0.2)' : 'transparent', border: '1px solid rgba(59, 130, 246, 0.3)', color: statusFilter === 'COMMITTEE' ? '#93c5fd' : 'var(--text-muted)' }}
            >
              {activeT.filter_committee}
            </button>
            <button 
              onClick={() => setStatusFilter('COMPLETED')} 
              style={{ padding: '0.25rem 0.6rem', borderRadius: '6px', fontSize: '0.75rem', fontWeight: 500, cursor: 'pointer', background: statusFilter === 'COMPLETED' ? 'rgba(59, 130, 246, 0.2)' : 'transparent', border: '1px solid rgba(59, 130, 246, 0.3)', color: statusFilter === 'COMPLETED' ? '#93c5fd' : 'var(--text-muted)' }}
            >
              {activeT.filter_completed}
            </button>
          </div>

          {/* List panel */}
          <div style={{ flex: 1, overflowY: 'auto', paddingRight: '4px' }}>
            {filteredPetitions.map(p => (
              <div 
                key={p.riigikogu_uuid} 
                onClick={() => setSelectedInitId(p.initiative_id || p.riigikogu_uuid)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  padding: '0.75rem',
                  borderRadius: '8px',
                  background: (selectedInitId === p.initiative_id || selectedInitId === p.riigikogu_uuid) ? 'rgba(59, 130, 246, 0.08)' : 'transparent',
                  border: '1px solid',
                  borderColor: (selectedInitId === p.initiative_id || selectedInitId === p.riigikogu_uuid) ? 'rgba(59, 130, 246, 0.2)' : 'rgba(255,255,255,0.03)',
                  cursor: 'pointer',
                  marginBottom: '0.5rem',
                  transition: 'all 0.2s'
                }}
              >
                <div style={{ flex: 1, minWidth: 0 }}>
                  <h4 style={{ fontSize: '0.88rem', fontWeight: 500, color: '#fff', marginBottom: '0.25rem', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {p.title}
                  </h4>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                    <span>{p.reference}</span>
                    <span>•</span>
                    <span>{p.submitting_date ? new Date(p.submitting_date).toLocaleDateString() : ''}</span>
                    <span className={getStatusBadgeClass(p.current_status)} style={{ fontSize: '0.65rem', padding: '1px 5px', fontWeight: 500 }}>
                      {p.current_status ? (lang === 'et' ? p.current_status : (p.current_status === 'Menetlus lõpetatud' ? 'Finished' : p.current_status === 'Arutelu komisjonis' ? 'In Committee' : 'Registered')) : ''}
                    </span>
                  </div>
                </div>
                <ChevronRight size={16} style={{ color: 'var(--text-muted)', opacity: 0.5, marginLeft: '0.5rem' }} />
              </div>
            ))}
          </div>
        </div>

        {/* RIGHT COLUMN: DETAILS */}
        <div className="glass-panel" style={{ display: 'flex', flexDirection: 'column', padding: '1.5rem', maxHeight: '650px', overflowY: 'auto', minWidth: 0 }}>
          {selectedDetails ? (
            <div>
              {/* Header Info */}
              <div style={{ borderBottom: '1px solid rgba(255,255,255,0.08)', paddingBottom: '1rem', marginBottom: '1.2rem' }}>
                <span className="badge" style={{ fontSize: '0.7rem', padding: '2px 8px', background: 'rgba(96, 165, 250, 0.1)', color: '#93c5fd', borderColor: 'rgba(96, 165, 250, 0.2)' }}>
                  {selectedDetails.petition.reference}
                </span>
                <h3 style={{ fontSize: '1.15rem', color: '#fff', marginTop: '0.5rem', marginBottom: '0.75rem', lineHeight: '1.4' }}>{selectedDetails.petition.title}</h3>
                
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: '0.8rem', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                  <div>
                    <strong style={{ color: '#fff', display: 'block', fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '2px' }}>{activeT.submitted_on}</strong>
                    <Calendar size={13} style={{ display: 'inline', verticalAlign: 'middle', marginRight: 3, marginTop: '-2px' }} />
                    {selectedDetails.petition.submitting_date ? new Date(selectedDetails.petition.submitting_date).toLocaleDateString() : '-'}
                  </div>
                  <div>
                    <strong style={{ color: '#fff', display: 'block', fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '2px' }}>{activeT.committee}</strong>
                    <Landmark size={13} style={{ display: 'inline', verticalAlign: 'middle', marginRight: 3, marginTop: '-2px' }} />
                    {selectedDetails.petition.responsible_committee || '-'}
                  </div>
                  <div>
                    <strong style={{ color: '#fff', display: 'block', fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '2px' }}>{activeT.outcome}</strong>
                    <Clock size={13} style={{ display: 'inline', verticalAlign: 'middle', marginRight: 3, marginTop: '-2px' }} />
                    <span style={{ color: selectedDetails.petition.current_status === 'Menetlus lõpetatud' ? '#c084fc' : '#eab308' }}>
                      {selectedDetails.petition.last_committee_decision || activeT.outcome_not_resolved}
                    </span>
                  </div>
                </div>
              </div>

              {/* Status Timeline */}
              <div style={{ marginBottom: '1.5rem' }}>
                <h4 style={{ fontSize: '0.95rem', color: '#fff', marginBottom: '0.8rem', borderLeft: '3px solid #3b82f6', paddingLeft: '8px' }}>
                  {activeT.timeline}
                </h4>
                <div style={{ paddingLeft: '8px', borderLeft: '1px solid rgba(255,255,255,0.06)', marginLeft: '6px' }}>
                  {selectedDetails.timeline.map((item, idx) => (
                    <div key={idx} style={{ position: 'relative', paddingBottom: '1rem', paddingLeft: '1.2rem' }}>
                      {/* Timeline dot */}
                      <span style={{
                        position: 'absolute',
                        left: '-22px',
                        top: '4px',
                        width: '9px',
                        height: '9px',
                        borderRadius: '50%',
                        backgroundColor: idx === selectedDetails.timeline.length - 1 ? '#3b82f6' : 'rgba(255,255,255,0.15)',
                        border: idx === selectedDetails.timeline.length - 1 ? '2px solid #60a5fa' : 'none'
                      }}></span>
                      
                      <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '1px' }}>
                        {new Date(item.date).toLocaleDateString()}
                      </div>
                      <div style={{ fontSize: '0.88rem', color: '#fff', fontWeight: 500 }}>
                        {lang === 'et' ? item.status_value : (item.status_code === 'REGISTREERITUD' ? 'Registered' : item.status_code === 'MENETLUSSE_VOETUD' ? 'Taken into proceedings' : item.status_code === 'ARUTELU_KOMISJONIS' ? 'Discussed in committee' : item.status_code === 'MENETLUS_LOPETATUD' ? 'Proceedings ended' : item.status_value)}
                      </div>
                      {item.committee_decision && (
                        <div style={{ fontSize: '0.8rem', color: '#60a5fa', background: 'rgba(59, 130, 246, 0.04)', padding: '4px 8px', borderRadius: '4px', marginTop: '4px', display: 'inline-block', border: '1px solid rgba(59, 130, 246, 0.1)' }}>
                          📝 {item.committee_decision}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              {/* Related Draft & Votings */}
              {selectedDetails.petition.has_draft ? (
                <div style={{ borderTop: '1px solid rgba(255,255,255,0.08)', paddingTop: '1.2rem' }}>
                  <h4 style={{ fontSize: '0.95rem', color: '#fff', marginBottom: '0.8rem', borderLeft: '3px solid #8b5cf6', paddingLeft: '8px' }}>
                    {activeT.draft_info}
                  </h4>
                  <div style={{ background: 'rgba(139, 92, 246, 0.03)', border: '1px solid rgba(139, 92, 246, 0.15)', borderRadius: '8px', padding: '1rem', marginBottom: '1rem' }}>
                    <div style={{ fontSize: '0.95rem', fontWeight: 600, color: '#fff', marginBottom: '0.25rem' }}>{selectedDetails.petition.draft_title}</div>
                    <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                      {activeT.draft_status}: <span style={{ color: '#a78bfa', fontWeight: 500 }}>{selectedDetails.petition.draft_status}</span>
                    </div>
                  </div>

                  <h5 style={{ fontSize: '0.85rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '0.6rem' }}>
                    {activeT.votings_title} ({selectedDetails.votings.length})
                  </h5>
                  
                  {selectedDetails.votings.length > 0 ? (
                    <div>
                      {selectedDetails.votings.map((voting) => (
                        <div 
                          key={voting.voting_id} 
                          style={{
                            background: 'rgba(255,255,255,0.02)',
                            border: '1px solid rgba(255,255,255,0.05)',
                            borderRadius: '8px',
                            padding: '0.8rem',
                            marginBottom: '0.5rem',
                            cursor: 'pointer'
                          }}
                          onClick={() => setExpandedVotingId(expandedVotingId === voting.voting_id ? null : voting.voting_id)}
                        >
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '0.5rem' }}>
                            <div>
                              <div style={{ fontSize: '0.88rem', fontWeight: 600, color: '#fff' }}>{voting.description}</div>
                              <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '2px' }}>{new Date(voting.session_date).toLocaleDateString()}</div>
                            </div>
                            <span className="badge" style={{
                              fontSize: '0.65rem',
                              padding: '1px 5px',
                              background: voting.result === 'PASSED' || voting.result === 'poolt' || voting.result === 'Vastu võetud' ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)',
                              color: voting.result === 'PASSED' || voting.result === 'poolt' || voting.result === 'Vastu võetud' ? '#10b981' : '#ef4444',
                              borderColor: voting.result === 'PASSED' || voting.result === 'poolt' || voting.result === 'Vastu võetud' ? 'rgba(16, 185, 129, 0.2)' : 'rgba(239, 68, 68, 0.2)'
                            }}>
                              {voting.result === 'poolt' || voting.result === 'Vastu võetud' ? (lang === 'et' ? 'Vastu võetud' : 'Passed') : (lang === 'et' ? 'Tagasi lükatud' : 'Failed')}
                            </span>
                          </div>

                          <div style={{ display: 'flex', gap: '1rem', marginTop: '0.6rem', fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                            <span>🟢 {activeT.in_favor}: <strong style={{ color: '#fff' }}>{voting.in_favor}</strong></span>
                            <span>🔴 {activeT.against}: <strong style={{ color: '#fff' }}>{voting.against}</strong></span>
                            <span>⚪ {activeT.neutral}: <strong style={{ color: '#fff' }}>{voting.neutral + voting.abstained}</strong></span>
                          </div>

                          {/* Expanded Faction Breakdown */}
                          {expandedVotingId === voting.voting_id && (
                            <div style={{ borderTop: '1px solid rgba(255,255,255,0.06)', marginTop: '0.8rem', paddingTop: '0.8rem' }} onClick={e => e.stopPropagation()}>
                              <div style={{ fontSize: '0.8rem', color: '#fff', fontWeight: 600, marginBottom: '0.6rem', display: 'flex', alignItems: 'center', gap: '4px' }}>
                                <Vote size={14} color="#a78bfa" />
                                {activeT.faction_breakdown}
                              </div>
                              
                              {Object.entries(voting.factions).map(([factionName, votes]) => {
                                const total = votes.poolt + votes.vastu + votes.erapooletu + votes.puudub;
                                if (total === 0) return null;
                                
                                const yesWidth = `${(votes.poolt / total) * 100}%`;
                                const noWidth = `${(votes.vastu / total) * 100}%`;
                                const neutralWidth = `${((votes.erapooletu + votes.puudub) / total) * 100}%`;
                                
                                return (
                                  <div key={factionName} style={{ marginBottom: '0.8rem' }}>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', marginBottom: '3px' }}>
                                      <span style={{ color: '#fff', fontWeight: 500, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', maxWidth: '75%' }}>{factionName}</span>
                                      <span style={{ color: 'var(--text-muted)' }}>
                                        {votes.poolt}/{votes.vastu}/{(votes.erapooletu + votes.puudub)} (tot: {total})
                                      </span>
                                    </div>
                                    
                                    {/* Horizontal Stacked Bar */}
                                    <div style={{ display: 'flex', height: '8px', borderRadius: '4px', overflow: 'hidden', background: 'rgba(255,255,255,0.05)' }}>
                                      <div style={{ width: yesWidth, background: '#10b981' }} title={`Yes: ${votes.poolt}`} />
                                      <div style={{ width: noWidth, background: '#ef4444' }} title={`No: ${votes.vastu}`} />
                                      <div style={{ width: neutralWidth, background: '#4b5563' }} title={`Abstain/Absent: ${votes.erapooletu + votes.puudub}`} />
                                    </div>
                                  </div>
                                );
                              })}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem', fontStyle: 'italic', padding: '0.5rem' }}>{activeT.no_votings}</div>
                  )}
                </div>
              ) : null}
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', minHeight: '300px', textAlign: 'center', color: 'var(--text-muted)' }}>
              <Landmark size={48} style={{ opacity: 0.15, marginBottom: '1rem' }} />
              <p style={{ maxWidth: '300px', fontSize: '0.9rem', lineHeight: '1.5' }}>
                {activeT.select_placeholder}
              </p>
            </div>
          )}
        </div>

      </div>
    </div>
  );
}
