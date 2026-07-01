// App.jsx — HireGenius AI Enterprise Dashboard

import { useEffect, useMemo, useState, useCallback } from 'react';
import {
  analyzeJD, exportRankingsUrl, getCandidates, getRankings,
  rankCandidates, getDashboardStats, getTalentInsights,
  getRankingDetail, API_BASE,
} from './api';
import JobDescriptionUploader from './components/JobDescriptionUploader';
import RankingTable from './components/RankingTable';
import ExplainabilityPanel from './components/ExplainabilityPanel';
import ExecutiveOverview from './components/ExecutiveOverview';
import AIInsightsPanel from './components/AIInsightsPanel';
import { TableSkeleton } from './components/SkeletonLoader';

// =============================================
// Sidebar navigation config
// =============================================
const NAV_ITEMS = [
  { id: 'overview', label: 'Executive Overview', icon: '📊' },
  { id: 'rank', label: 'Rank Candidates', icon: '⚡' },
  { id: 'history', label: 'Ranking History', icon: '📋' },
  { id: 'insights', label: 'AI Insights', icon: '🧠' },
];

// =============================================
// Helper components
// =============================================

function Sidebar({ activeView, onNavigate }) {
  return (
    <aside className="sidebar">
      {/* Logo */}
      <div className="sidebar-logo">
        <div className="sidebar-logo-mark">
          <div className="logo-icon">⚡</div>
          <div>
            <div className="logo-text">HireGenius AI</div>
            <div className="logo-tagline">Beyond Keywords. Intelligent Hiring.</div>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="sidebar-nav">
        <div className="nav-section-label">Main</div>
        {NAV_ITEMS.map(item => (
          <button
            key={item.id}
            className={`nav-item ${activeView === item.id ? 'active' : ''}`}
            onClick={() => onNavigate(item.id)}
            id={`nav-${item.id}`}
          >
            <span className="nav-item-icon">{item.icon}</span>
            {item.label}
          </button>
        ))}

        <div className="nav-section-label" style={{ marginTop: '16px' }}>Resources</div>
        <a
          href={API_BASE.endsWith('/api') ? `${API_BASE}/docs/` : `${API_BASE}/api/docs/`}
          target="_blank"
          rel="noopener noreferrer"
          className="nav-item"
        >
          <span className="nav-item-icon">📖</span>
          API Documentation
        </a>
      </nav>

      {/* Footer badge */}
      <div className="sidebar-footer">
        <div style={{
          padding: '10px 12px', background: 'rgba(99,102,241,0.08)',
          borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)',
        }}>
          <div style={{ fontSize: '11px', color: 'var(--brand-primary)', fontWeight: '700', marginBottom: '4px' }}>
            ⚡ Multi-Agent AI v2.0
          </div>
          <div style={{ fontSize: '10px', color: 'var(--text-muted)', lineHeight: '1.4' }}>
            5 specialized evaluator agents · Dynamic role weights · Explainable rankings
          </div>
        </div>
      </div>
    </aside>
  );
}

function Topbar({ activeView, latestJobId, rankingCount, stats }) {
  const titles = {
    overview: { title: 'Executive Overview', subtitle: 'Hiring intelligence at a glance' },
    rank: { title: 'Rank Candidates', subtitle: 'AI-powered multi-agent evaluation' },
    history: { title: 'Ranking History', subtitle: 'Previous ranking sessions' },
    insights: { title: 'AI Talent Insights', subtitle: 'Market intelligence and skill trends' },
  };
  const { title, subtitle } = titles[activeView] || titles.overview;

  return (
    <div className="topbar">
      <div>
        <div className="topbar-title">{title}</div>
        <div className="topbar-subtitle">{subtitle}</div>
      </div>
      <div className="topbar-actions">
        {rankingCount > 0 && (
          <span style={{
            fontSize: '12px', color: 'var(--text-muted)',
            padding: '4px 10px', background: 'var(--bg-elevated)',
            borderRadius: 'var(--radius-full)', border: '1px solid var(--border-subtle)',
          }}>
            {rankingCount} ranked
          </span>
        )}
        {latestJobId && (
          <a
            href={exportRankingsUrl(latestJobId, 'full')}
            className="btn btn-secondary btn-sm"
            id="export-csv-btn"
          >
            ⬇️ Export CSV
          </a>
        )}
        {latestJobId && (
          <a
            href={exportRankingsUrl(latestJobId, 'submission')}
            className="btn btn-ghost btn-sm"
            id="export-submission-btn"
          >
            📄 Submission CSV
          </a>
        )}
      </div>
    </div>
  );
}

function JobSummaryCard({ summary, jobTitle, roleType, weightsUsed }) {
  if (!summary) return null;

  const ROLE_LABELS = {
    backend: '⚙️ Backend Engineering',
    frontend: '🎨 Frontend Engineering',
    leadership: '👥 Leadership / Management',
    research: '🔬 Research / ML',
    data: '📊 Data Engineering',
    design: '🖌️ Design / UX',
    general: '💼 General',
  };

  const skillsToShow = [
    ...(summary.required_skills || []).slice(0, 5),
  ];

  return (
    <div className="card">
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
        <span style={{ fontSize: '16px' }}>🎯</span>
        <div style={{ fontSize: '14px', fontWeight: '600', color: 'var(--text-primary)' }}>
          Job Intelligence Summary
        </div>
        {roleType && (
          <span className="badge badge-primary" style={{ marginLeft: 'auto' }}>
            {ROLE_LABELS[roleType] || roleType}
          </span>
        )}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', fontSize: '13px' }}>
        <div style={{ padding: '10px', background: 'var(--bg-elevated)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
          <div style={{ color: 'var(--text-muted)', marginBottom: '6px', fontSize: '11px', fontWeight: '600', textTransform: 'uppercase' }}>Required Skills</div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
            {skillsToShow.length > 0
              ? skillsToShow.map((s, i) => (
                <span key={i} className="skill-tag skill-tag-matched" style={{ fontSize: '10px' }}>{s}</span>
              ))
              : <span style={{ color: 'var(--text-muted)' }}>Analyzing…</span>
            }
          </div>
        </div>

        <div style={{ padding: '10px', background: 'var(--bg-elevated)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
          <div style={{ color: 'var(--text-muted)', marginBottom: '6px', fontSize: '11px', fontWeight: '600', textTransform: 'uppercase' }}>Role Signals</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
            {summary.experience_years && (
              <div style={{ color: 'var(--text-secondary)', fontSize: '12px' }}>
                📅 {summary.experience_years}+ years exp required
              </div>
            )}
            {summary.seniority && (
              <div style={{ color: 'var(--text-secondary)', fontSize: '12px' }}>
                🎖️ {summary.seniority.charAt(0).toUpperCase() + summary.seniority.slice(1)} level
              </div>
            )}
            {summary.industry && (
              <div style={{ color: 'var(--text-secondary)', fontSize: '12px' }}>
                🏢 {summary.industry.charAt(0).toUpperCase() + summary.industry.slice(1)} industry
              </div>
            )}
          </div>
        </div>

        {summary.behavioral_traits && summary.behavioral_traits.length > 0 && (
          <div style={{ padding: '10px', background: 'var(--bg-elevated)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)', gridColumn: '1 / -1' }}>
            <div style={{ color: 'var(--text-muted)', marginBottom: '6px', fontSize: '11px', fontWeight: '600', textTransform: 'uppercase' }}>Behavioral Traits Expected</div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
              {summary.behavioral_traits.map((t, i) => (
                <span key={i} className="badge badge-neutral" style={{ fontSize: '10px' }}>{t}</span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Dynamic weights used */}
      {weightsUsed && (
        <div style={{ marginTop: '12px', padding: '10px 12px', background: 'rgba(99,102,241,0.06)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
          <div style={{ fontSize: '11px', color: 'var(--brand-primary)', fontWeight: '600', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '4px' }}>
            ⚖️ Dynamic Role Weights Applied
          </div>
          <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
            {Object.entries(weightsUsed).map(([key, val]) => (
              <div key={key} style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '11px' }}>
                <span style={{ color: 'var(--text-muted)', textTransform: 'capitalize' }}>{key}:</span>
                <span style={{ color: 'var(--brand-primary)', fontWeight: '700' }}>{Math.round(val * 100)}%</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function HistoryView({ rankings, onLoadRanking }) {
  if (!rankings || !rankings.length) {
    return (
      <div className="card">
        <div className="empty-state">
          <div className="empty-state-icon">📋</div>
          <div className="empty-state-title">No History Yet</div>
          <div className="empty-state-desc">Previous ranking sessions will appear here.</div>
        </div>
      </div>
    );
  }

  return (
    <div className="card">
      <div className="section-header">
        <div>
          <div className="section-title">📋 Ranking History</div>
          <div className="section-subtitle">Previous AI ranking sessions</div>
        </div>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        {rankings.map((job, i) => (
          <div
            key={job.id}
            onClick={() => onLoadRanking(job)}
            style={{
              display: 'flex', alignItems: 'center', gap: '14px', padding: '14px 16px',
              background: 'var(--bg-elevated)', borderRadius: 'var(--radius-md)',
              border: '1px solid var(--border-subtle)', cursor: 'pointer',
              transition: 'var(--transition-fast)',
            }}
            onMouseEnter={e => { e.currentTarget.style.borderColor = 'var(--brand-primary)'; e.currentTarget.style.background = 'var(--bg-hover)'; }}
            onMouseLeave={e => { e.currentTarget.style.borderColor = 'var(--border-subtle)'; e.currentTarget.style.background = 'var(--bg-elevated)'; }}
          >
            <div style={{
              width: '40px', height: '40px', borderRadius: 'var(--radius-md)',
              background: 'var(--gradient-brand)', display: 'flex', alignItems: 'center',
              justifyContent: 'center', fontSize: '18px', flexShrink: 0,
            }}>
              ⚡
            </div>
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{ fontWeight: '600', color: 'var(--text-primary)', fontSize: '14px', marginBottom: '3px' }}>
                {job.title || 'Untitled Role'}
              </div>
              <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                {job.result_count || 0} candidates ranked · {job.role_type || 'general'} role
              </div>
            </div>
            <div style={{ textAlign: 'right', flexShrink: 0 }}>
              {job.top_candidate_name && (
                <div style={{ fontSize: '13px', fontWeight: '600', color: 'var(--brand-success)' }}>
                  🏆 {job.top_candidate_name}
                </div>
              )}
              {job.top_score != null && (
                <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Score: {job.top_score}</div>
              )}
              <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '4px' }}>
                {job.created_at ? new Date(job.created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }) : ''}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// =============================================
// Main App
// =============================================
function App() {
  const [activeView, setActiveView] = useState('overview');
  const [panelTab, setPanelTab] = useState('Overview');

  // JD state
  const [jobTitle, setJobTitle] = useState('');
  const [jobDescription, setJobDescription] = useState('');
  const [summary, setSummary] = useState(null);
  const [roleType, setRoleType] = useState('general');
  const [weightsUsed, setWeightsUsed] = useState(null);

  // Ranking state
  const [rankings, setRankings] = useState([]);
  const [selected, setSelected] = useState(null);
  const [latestJobId, setLatestJobId] = useState(null);
  const [rankingHistory, setRankingHistory] = useState([]);

  // Stats
  const [stats, setStats] = useState(null);
  const [statsLoading, setStatsLoading] = useState(false);

  // UI state
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const topCandidate = useMemo(() => rankings[0] || null, [rankings]);
  const selectedCandidate = selected || topCandidate;

  const loadStats = useCallback(() => {
    setStatsLoading(true);
    getDashboardStats()
      .then(setStats)
      .catch(() => {})
      .finally(() => setStatsLoading(false));
  }, []);

  useEffect(() => {
    // Load initial data
    getCandidates().catch(() => {});
    getRankings()
      .then(jobs => {
        if (jobs && jobs.length > 0) {
          setRankingHistory(jobs);
        }
      })
      .catch(() => {});
    loadStats();
  }, []);

  const handleSubmit = async ({ job_title, job_description, top_k }) => {
    setLoading(true);
    setError('');
    setJobTitle(job_title);
    setJobDescription(job_description);
    try {
      // Analyze JD
      const jdData = await analyzeJD(job_title, job_description);
      setSummary(jdData);
      setRoleType(jdData.role_type || 'general');

      // Rank candidates
      const rankData = await rankCandidates({ job_title, job_description, top_k });
      setLatestJobId(rankData.id || null);
      setRankings(rankData.results || []);
      setSelected(rankData.results?.[0] || null);
      setWeightsUsed(rankData.weights_used || null);

      // Refresh stats
      loadStats();

      // Refresh history
      getRankings().then(jobs => jobs && setRankingHistory(jobs)).catch(() => {});

      // Switch to rank view
      setActiveView('rank');
    } catch (err) {
      setError(err.message || 'An error occurred during ranking.');
    } finally {
      setLoading(false);
    }
  };

  const handleLoadRanking = async (job) => {
    setLoading(true);
    setError('');
    try {
      const fullJob = await getRankingDetail(job.id);
      setJobTitle(fullJob.title || '');
      setJobDescription(fullJob.job_description || '');
      setSummary(fullJob.job_analysis || null);
      setRoleType(fullJob.role_type || 'general');
      setWeightsUsed(fullJob.weights_used || null);
      setRankings(fullJob.results || []);
      setSelected(fullJob.results?.[0] || null);
      setLatestJobId(fullJob.id);
      setActiveView('rank');
    } catch (err) {
      setError(err.message || 'Failed to load ranking details.');
    } finally {
      setLoading(false);
    }
  };

  const handleExportExcel = async () => {
    if (!latestJobId) return;
    try {
      const response = await fetch(`${API_BASE}/export/${latestJobId}/`, {
        method: 'GET',
      });
      if (!response.ok) {
        throw new Error(`Export failed: ${response.statusText}`);
      }
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'submission.xlsx';
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError(err.message || 'Failed to export results.');
    }
  };

  const handleSelectCandidate = (candidate) => {
    setSelected(candidate);
    setPanelTab('Overview');
  };

  return (
    <div className="app-wrapper">
      <Sidebar activeView={activeView} onNavigate={setActiveView} />

      <div className="main-content">
        <Topbar
          activeView={activeView}
          latestJobId={latestJobId}
          rankingCount={rankings.length}
          stats={stats}
        />

        <div className="page-content">
          {/* Error alert */}
          {error && (
            <div className="alert alert-error" style={{ marginBottom: '20px' }}>
              <span>⚠️</span>
              <div>
                <div style={{ fontWeight: '600', marginBottom: '4px' }}>Error</div>
                <div style={{ fontSize: '13px' }}>{error}</div>
              </div>
              <button
                onClick={() => setError('')}
                style={{ marginLeft: 'auto', background: 'none', border: 'none', color: 'inherit', cursor: 'pointer', fontSize: '16px', padding: '0 4px' }}
              >
                ✕
              </button>
            </div>
          )}

          {/* ===== OVERVIEW VIEW ===== */}
          {activeView === 'overview' && (
            <div className="fade-in">
              {/* Welcome banner */}
              <div style={{
                padding: '24px 28px', borderRadius: 'var(--radius-xl)',
                background: 'linear-gradient(135deg, rgba(99,102,241,0.12) 0%, rgba(139,92,246,0.12) 100%)',
                border: '1px solid var(--border-default)',
                marginBottom: '24px',
                position: 'relative', overflow: 'hidden',
              }}>
                <div style={{
                  position: 'absolute', top: '-20px', right: '-20px',
                  width: '200px', height: '200px',
                  background: 'radial-gradient(circle, rgba(99,102,241,0.15) 0%, transparent 70%)',
                  pointerEvents: 'none',
                }} />
                <div style={{ position: 'relative' }}>
                  <div style={{ fontSize: '11px', color: 'var(--brand-primary)', textTransform: 'uppercase', letterSpacing: '0.1em', fontWeight: '600', marginBottom: '8px' }}>
                    HireGenius AI · Recruitment Intelligence Platform
                  </div>
                  <h1 style={{ fontSize: '26px', fontWeight: '800', color: 'var(--text-primary)', marginBottom: '8px', letterSpacing: '-0.02em' }}>
                    Beyond Keywords. Intelligent Hiring Starts Here.
                  </h1>
                  <p style={{ fontSize: '14px', color: 'var(--text-secondary)', maxWidth: '600px', lineHeight: '1.6' }}>
                    5 specialized AI agents evaluate every candidate across Skills, Experience, Behavior, Potential, and Role Alignment.
                    Explainable, bias-aware, and built for enterprise-grade hiring decisions.
                  </p>
                  <div style={{ display: 'flex', gap: '12px', marginTop: '16px', flexWrap: 'wrap' }}>
                    <button
                      className="btn btn-primary"
                      onClick={() => setActiveView('rank')}
                      id="start-ranking-btn"
                    >
                      ⚡ Start Ranking
                    </button>
                    <button
                      className="btn btn-secondary"
                      onClick={() => setActiveView('insights')}
                    >
                      🧠 View AI Insights
                    </button>
                  </div>
                </div>
              </div>

              <ExecutiveOverview stats={stats} loading={statsLoading} />
            </div>
          )}

          {/* ===== RANK VIEW ===== */}
          {activeView === 'rank' && (
            <div className="fade-in">
              <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                {/* Job Input */}
                <JobDescriptionUploader
                  jobTitle={jobTitle}
                  jobDescription={jobDescription}
                  loading={loading}
                  onSubmit={handleSubmit}
                  rankings={rankings}
                  onExportExcel={handleExportExcel}
                  latestJobId={latestJobId}
                />

                {/* JD Summary */}
                {summary && (
                  <JobSummaryCard
                    summary={summary}
                    jobTitle={jobTitle}
                    roleType={roleType}
                    weightsUsed={weightsUsed}
                  />
                )}

                {/* Main panel split: rankings + explainability */}
                {loading && rankings.length === 0 && (
                  <TableSkeleton rows={8} cols={5} />
                )}

                {!loading && rankings.length === 0 && summary && (
                  <div className="empty-state">
                    <h3>No candidates ranked yet</h3>
                    <p style={{ fontSize: '13px' }}>Adjust your job description or increase top-K to see matches.</p>
                  </div>
                )}

                {rankings.length > 0 && (
                  <div className="panel-split">
                    {/* Left: Rankings */}
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                      <div className="card">
                        <div className="section-header">
                          <div>
                            <div className="section-title">
                              🏆 Ranked Candidates
                              {roleType && roleType !== 'general' && (
                                <span className="badge badge-primary" style={{ marginLeft: '10px', fontSize: '10px' }}>
                                  {roleType}
                                </span>
                              )}
                            </div>
                            <div className="section-subtitle">
                              Click any candidate to view full AI evaluation report
                            </div>
                          </div>
                        </div>
                        <RankingTable
                          rankings={rankings}
                          onSelect={handleSelectCandidate}
                          selectedId={selectedCandidate?.candidate?.id}
                        />
                      </div>
                    </div>

                    {/* Right: Explainability */}
                    <div>
                      <ExplainabilityPanel
                        candidate={selectedCandidate}
                        activeTab={panelTab}
                        onTabChange={setPanelTab}
                      />
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* ===== HISTORY VIEW ===== */}
          {activeView === 'history' && (
            <div className="fade-in">
              <HistoryView
                rankings={rankingHistory}
                onLoadRanking={handleLoadRanking}
              />
            </div>
          )}

          {/* ===== INSIGHTS VIEW ===== */}
          {activeView === 'insights' && (
            <div className="fade-in">
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
                {['general', 'backend', 'research', 'leadership'].map(rt => (
                  <AIInsightsPanel key={rt} roleType={rt} jobDescription={jobDescription} />
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div style={{
          padding: '16px 32px', borderTop: '1px solid var(--border-subtle)',
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          fontSize: '12px', color: 'var(--text-muted)',
        }}>
          <span>HireGenius AI v2.0 · Beyond Keywords. Intelligent Hiring Starts Here.</span>
          <span>Multi-Agent AI · Explainable Rankings · Enterprise-Grade</span>
        </div>
      </div>
    </div>
  );
}

export default App;
