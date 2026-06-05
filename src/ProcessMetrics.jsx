import { useState, useEffect, useRef } from 'react';
import { Clock, Search, AlertCircle, CheckCircle2, Calendar, ChevronRight, PlayCircle, FileText } from 'lucide-react';

export default function ProcessMetrics({ lang }) {
  const [metrics, setMetrics] = useState(null);
  const [allInitiatives, setAllInitiatives] = useState([]);
  const [topTimelines, setTopTimelines] = useState({});
  const [searchQuery, setSearchQuery] = useState('');
  const [showDropdown, setShowDropdown] = useState(false);
  const [selectedId, setSelectedId] = useState('');
  const [selectedTitle, setSelectedTitle] = useState('');
  const [timeline, setTimeline] = useState([]);
  const [loadingTimeline, setLoadingTimeline] = useState(false);
  const dropdownRef = useRef(null);

  const t = {
    en: {
      title: "Process Analytics & Lifecycle Timelines",
      subtitle: "Understand how civic requests move through the decision system",
      stalled_warning: "Initiatives remain stuck in bureaucracy",
      median_days: "days (median)",
      created: "Created",
      threshold: "1,000 Signatures Reached",
      parliament: "Sent to Parliament",
      completed: "Completed / Done",
      search_placeholder: "Search all 1,000+ initiatives by title...",
      no_timeline_data: "No event timeline available for this initiative.",
      select_prompt: "Select an initiative above to inspect its historical event timeline.",
      loading: "Loading timeline...",
      stage_durations: "Stage Transition Durations",
      stalled_rate: "Stalled Rate",
      active_in_review: "Active in review",
      stalled_desc: "12+ months without any public event update",
      event_date: "Event Date",
      actor: "Actor",
      timeline_title: "Lifecycle Event Log",
      milestone_100: "100 Signatures Milestone",
      milestone_1000: "1,000 Signatures Milestone",
      sent_to_parliament: "Sent to Riigikogu",
      sent_to_government: "Sent to Government",
      finished_in_government: "Processed by Government",
      parliament_finished: "Riigikogu Review Finished",
      other_event: "Platform Event"
    },
    et: {
      title: "Protsessi analüüs ja elutsükli ajajooned",
      subtitle: "Saage aru, kuidas kodanikualgatused otsustussüsteemis liiguvad",
      stalled_warning: "algatust on jäänud bürokraatiasse kinni",
      median_days: "päeva (mediaan)",
      created: "Loodud",
      threshold: "1000 allkirja koos",
      parliament: "Saadetud parlamenti",
      completed: "Lõpetatud / Tehtud",
      search_placeholder: "Otsi 1000+ algatuse seast pealkirja järgi...",
      no_timeline_data: "Selle algatuse kohta puuduvad sündmuste andmed.",
      select_prompt: "Valige ülevalt algatus, et näha selle elutsükli ajajoont.",
      loading: "Ajajoone laadimine...",
      stage_durations: "Etappide läbimise kestus",
      stalled_rate: "Seisvate algatuste määr",
      active_in_review: "Aktiivses menetluses",
      stalled_desc: "12+ kuud ilma ühegi avaliku sündmuseta",
      event_date: "Sündmuse kuupäev",
      actor: "Osapool",
      timeline_title: "Elutsükli sündmuste logi",
      milestone_100: "100 allkirja künnis",
      milestone_1000: "1000 allkirja künnis",
      sent_to_parliament: "Saadetud Riigikogusse",
      sent_to_government: "Saadetud Valitsusele",
      finished_in_government: "Valitsuses menetletud",
      parliament_finished: "Riigikogu menetlus lõpetatud",
      other_event: "Platvormi sündmus"
    }
  };

  const activeT = t[lang];

  useEffect(() => {
    async function loadProcessData() {
      try {
        const [metricsRes, listRes, topRes] = await Promise.all([
          fetch('/api_data/process_metrics.json'),
          fetch('/api_data/initiatives_list.json'),
          fetch('/api_data/top_timelines.json')
        ]);
        
        setMetrics(await metricsRes.json());
        setAllInitiatives(await listRes.json());
        setTopTimelines(await topRes.json());
      } catch (err) {
        console.error("Error loading process metrics:", err);
      }
    }
    loadProcessData();
  }, []);

  // Close dropdown on click outside
  useEffect(() => {
    function handleClickOutside(event) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setShowDropdown(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // Fetch or load timeline when ID changes
  const handleSelectInitiative = async (init) => {
    setSelectedId(init.id);
    setSelectedTitle(init.title);
    setSearchQuery(init.title);
    setShowDropdown(false);
    setLoadingTimeline(true);
    setTimeline([]);

    try {
      // Check if we have it preloaded in topTimelines
      if (topTimelines[init.id]) {
        setTimeline(topTimelines[init.id].events || []);
      } else {
        // Fetch dynamically from server fallback
        const res = await fetch(`/api/initiatives/${init.id}/timeline`);
        const data = await res.json();
        setTimeline(data || []);
      }
    } catch (err) {
      console.error("Error fetching timeline:", err);
    } finally {
      setLoadingTimeline(false);
    }
  };

  const filteredInitiatives = searchQuery
    ? allInitiatives.filter(i => i.title.toLowerCase().includes(searchQuery.toLowerCase())).slice(0, 10)
    : allInitiatives.slice(0, 10);

  const getEventName = (type, title) => {
    if (type === 'milestone-100') return activeT.milestone_100;
    if (type === 'milestone-1000') return activeT.milestone_1000;
    if (type === 'sent-to-parliament') return activeT.sent_to_parliament;
    if (type === 'sent-to-government') return activeT.sent_to_government;
    if (type === 'finished-in-government') return activeT.finished_in_government;
    if (type === 'parliament-finished') return activeT.parliament_finished;
    return title || activeT.other_event;
  };

  const getEventIcon = (type) => {
    if (type === 'milestone-100') return <FileText size={16} color="#3b82f6" />;
    if (type === 'milestone-1000') return <CheckCircle2 size={16} color="#10b981" />;
    if (type === 'sent-to-parliament' || type === 'sent-to-government') return <Clock size={16} color="#f59e0b" />;
    if (type === 'finished-in-government' || type === 'parliament-finished') return <CheckCircle2 size={16} color="#8b5cf6" />;
    return <PlayCircle size={16} color="#94a3b8" />;
  };

  return (
    <div style={{ marginTop: '1rem', marginBottom: '1rem' }}>
      <div className="glass-panel" style={{ padding: '2rem' }}>
        <h2 className="section-title" style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '0.5rem' }}>
          <Clock size={22} color="#a78bfa" /> {activeT.title}
        </h2>
        <p style={{ color: 'var(--text-muted, #94a3b8)', fontSize: '0.95rem', marginBottom: '2rem' }}>{activeT.subtitle}</p>

        {metrics && (
          <div className="dashboard-grid" style={{ gridTemplateColumns: '2fr 1fr', gap: '1.5rem', marginBottom: '2.5rem' }}>
            
            {/* Left Box: Stage durations */}
            <div style={{ background: 'rgba(255,255,255,0.02)', padding: '1.2rem', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.05)' }}>
              <h3 style={{ fontSize: '1rem', color: '#fff', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Clock size={16} color="#3b82f6" /> {activeT.stage_durations}
              </h3>
              
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1.2rem' }}>
                {/* Step 1 */}
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '0.4rem' }}>
                    <span style={{ color: '#fff', fontWeight: 500 }}>{activeT.created} → {activeT.threshold}</span>
                    <span style={{ color: '#10b981', fontWeight: 600 }}>{metrics.median_days_to_threshold} {activeT.median_days}</span>
                  </div>
                  <div style={{ height: '6px', background: 'rgba(255,255,255,0.05)', borderRadius: '3px', overflow: 'hidden' }}>
                    <div style={{ height: '100%', width: '15%', background: 'linear-gradient(90deg, #3b82f6, #10b981)', borderRadius: '3px' }}></div>
                  </div>
                </div>

                {/* Step 2 */}
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '0.4rem' }}>
                    <span style={{ color: '#fff', fontWeight: 500 }}>{activeT.threshold} → {activeT.parliament}</span>
                    <span style={{ color: '#f59e0b', fontWeight: 600 }}>{metrics.median_days_to_parliament} {activeT.median_days}</span>
                  </div>
                  <div style={{ height: '6px', background: 'rgba(255,255,255,0.05)', borderRadius: '3px', overflow: 'hidden' }}>
                    <div style={{ height: '100%', width: '45%', background: 'linear-gradient(90deg, #10b981, #f59e0b)', borderRadius: '3px' }}></div>
                  </div>
                </div>

                {/* Step 3 */}
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '0.4rem' }}>
                    <span style={{ color: '#fff', fontWeight: 500 }}>{activeT.parliament} → {activeT.completed}</span>
                    <span style={{ color: '#8b5cf6', fontWeight: 600 }}>{metrics.median_days_in_parliament} {activeT.median_days}</span>
                  </div>
                  <div style={{ height: '6px', background: 'rgba(255,255,255,0.05)', borderRadius: '3px', overflow: 'hidden' }}>
                    <div style={{ height: '100%', width: '100%', background: 'linear-gradient(90deg, #f59e0b, #8b5cf6)', borderRadius: '3px' }}></div>
                  </div>
                </div>
              </div>
            </div>

            {/* Right Box: Stalled rate */}
            <div style={{ background: 'rgba(239, 68, 68, 0.02)', padding: '1.2rem', borderRadius: '12px', border: '1px solid rgba(239, 68, 68, 0.1)', display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', textAlign: 'center' }}>
              <AlertCircle size={32} color="#f87171" style={{ marginBottom: '0.8rem' }} />
              <div style={{ fontSize: '0.9rem', color: 'var(--text-muted)', marginBottom: '0.2rem' }}>{activeT.stalled_rate}</div>
              <div style={{ fontSize: '2.5rem', fontWeight: 800, color: '#ef4444', lineHeight: 1 }}>{metrics.stalled_ratio}%</div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.6rem', lineHeight: '1.4' }}>
                <strong>{metrics.stalled_count} / {metrics.total_in_progress}</strong> {activeT.active_in_review}
                <br />
                <span style={{ fontSize: '0.75rem', opacity: 0.8 }}>({activeT.stalled_desc})</span>
              </div>
            </div>
          </div>
        )}

        {/* Section: Search Autocomplete */}
        <div style={{ position: 'relative', marginBottom: '2rem' }} ref={dropdownRef}>
          <div style={{ display: 'flex', alignItems: 'center', background: 'rgba(255,255,255,0.03)', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.1)', padding: '0.5rem 1rem' }}>
            <Search size={18} color="var(--text-muted)" style={{ marginRight: '0.8rem' }} />
            <input
              type="text"
              placeholder={activeT.search_placeholder}
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value);
                setShowDropdown(true);
              }}
              onFocus={() => setShowDropdown(true)}
              style={{
                width: '100%',
                background: 'none',
                border: 'none',
                color: '#fff',
                fontSize: '0.95rem',
                outline: 'none'
              }}
            />
          </div>

          {showDropdown && filteredInitiatives.length > 0 && (
            <div style={{
              position: 'absolute',
              top: '100%',
              left: 0,
              right: 0,
              background: 'rgba(15, 23, 42, 0.98)',
              border: '1px solid rgba(59, 130, 246, 0.3)',
              borderRadius: '8px',
              marginTop: '4px',
              boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.8)',
              zIndex: 99,
              maxHeight: '300px',
              overflowY: 'auto'
            }}>
              {filteredInitiatives.map(item => (
                <div
                  key={item.id}
                  onClick={() => handleSelectInitiative(item)}
                  style={{
                    padding: '0.8rem 1.2rem',
                    cursor: 'pointer',
                    borderBottom: '1px solid rgba(255,255,255,0.05)',
                    color: '#e2e8f0',
                    fontSize: '0.9rem',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center'
                  }}
                  onMouseEnter={(e) => e.target.style.background = 'rgba(59, 130, 246, 0.15)'}
                  onMouseLeave={(e) => e.target.style.background = 'none'}
                >
                  <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', maxWidth: '80%' }}>
                    {item.title}
                  </span>
                  <span style={{ fontSize: '0.7rem', padding: '0.1rem 0.4rem', borderRadius: '4px', background: 'rgba(255,255,255,0.08)', color: 'var(--text-muted)' }}>
                    {item.phase}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Section: Timeline Display */}
        <div style={{ background: 'rgba(0,0,0,0.15)', borderRadius: '12px', padding: '1.5rem', minHeight: '180px', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
          {selectedId ? (
            <div>
              <h3 style={{ fontSize: '1.1rem', color: '#fff', marginBottom: '2rem', display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                <Calendar size={18} color="#a78bfa" /> {activeT.timeline_title}
                <span style={{ fontSize: '0.85rem', fontWeight: 400, color: 'var(--text-muted)' }}>• {selectedTitle}</span>
              </h3>

              {loadingTimeline ? (
                <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>{activeT.loading}</div>
              ) : timeline.length > 0 ? (
                /* Vertical Timeline Layout */
                <div style={{ position: 'relative', paddingLeft: '2.5rem', borderLeft: '2px solid rgba(255, 255, 255, 0.08)', marginLeft: '10px' }}>
                  {timeline.map((event, idx) => (
                    <div key={event.event_id || idx} style={{ position: 'relative', marginBottom: '2rem' }}>
                      {/* Left Dot Icon Wrapper */}
                      <div style={{
                        position: 'absolute',
                        left: '-3.2rem',
                        top: '2px',
                        background: '#1e293b',
                        border: '2px solid rgba(255,255,255,0.15)',
                        borderRadius: '50%',
                        width: '28px',
                        height: '28px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.4)'
                      }}>
                        {getEventIcon(event.event_type)}
                      </div>

                      {/* Content Card */}
                      <div style={{ background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.04)', borderRadius: '8px', padding: '1rem', maxWidth: '700px' }}>
                        <h4 style={{ color: '#fff', fontSize: '0.95rem', margin: '0 0 0.5rem 0' }}>
                          {getEventName(event.event_type, event.event_title)}
                        </h4>
                        
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1rem', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                          <span>
                            <strong>{activeT.event_date}:</strong> {new Date(event.event_date).toLocaleDateString()}
                          </span>
                          {event.actor && (
                            <span>
                              <strong>{activeT.actor}:</strong> {event.actor}
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>{activeT.no_timeline_data}</div>
              )}
            </div>
          ) : (
            <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)', fontSize: '0.95rem' }}>
              <Clock size={36} color="var(--text-muted)" style={{ margin: '0 auto 0.8rem auto', opacity: 0.5, display: 'block' }} />
              {activeT.select_prompt}
            </div>
          )}
        </div>

      </div>
    </div>
  );
}
