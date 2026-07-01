// ExecutiveOverview.jsx — Executive Dashboard Stats & Hiring Funnel

function StatCard({ icon, label, value, trend, trendLabel, bgGradient, iconBg }) {
  return (
    <div className="stat-card" style={{ background: bgGradient || 'var(--bg-card)' }}>
      <div className="stat-card-icon" style={{ background: iconBg || 'rgba(99,102,241,0.15)' }}>
        {icon}
      </div>
      <div className="stat-card-value">{value ?? '—'}</div>
      <div className="stat-card-label">{label}</div>
      {trendLabel && (
        <div className={`stat-card-trend ${trend === 'up' ? 'trend-up' : 'trend-down'}`}>
          {trend === 'up' ? '↑' : '↓'} {trendLabel}
        </div>
      )}
    </div>
  );
}

function HiringFunnel({ funnel = [] }) {
  if (!funnel.length) return (
    <div className="empty-state" style={{ padding: '32px' }}>
      <div style={{ fontSize: '32px', marginBottom: '8px' }}>📊</div>
      <p style={{ fontSize: '14px', color: 'var(--text-muted)' }}>Run a ranking to see the hiring funnel.</p>
    </div>
  );

  const maxScore = Math.max(...funnel.map(f => f.score), 1);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
      {funnel.map((f, i) => {
        const width = (f.score / maxScore) * 100;
        const isStrong = (f.recommendation || '').toLowerCase().includes('strong');
        const isWeak = (f.recommendation || '').toLowerCase().includes('weak');
        const barColor = isStrong ? '#10b981' : isWeak ? '#ef4444' : '#6366f1';

        return (
          <div key={i} style={{
            padding: '12px 16px', background: 'var(--bg-elevated)',
            borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)',
            position: 'relative', overflow: 'hidden',
          }}>
            {/* Progress background */}
            <div style={{
              position: 'absolute', top: 0, left: 0, bottom: 0,
              width: `${width}%`,
              background: `${barColor}10`,
              transition: 'width 0.8s ease',
            }} />
            <div style={{ position: 'relative', display: 'flex', alignItems: 'center', gap: '12px' }}>
              <div style={{
                width: '24px', height: '24px', borderRadius: '50%',
                background: i === 0 ? 'linear-gradient(135deg,#f59e0b,#d97706)' :
                            i === 1 ? 'linear-gradient(135deg,#94a3b8,#64748b)' :
                            i === 2 ? 'linear-gradient(135deg,#f97316,#ea580c)' :
                            'var(--bg-card)',
                color: 'white', display: 'flex', alignItems: 'center',
                justifyContent: 'center', fontSize: '11px', fontWeight: '700', flexShrink: 0,
              }}>
                {f.rank}
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: '13px', fontWeight: '600', color: 'var(--text-primary)' }}>{f.name}</div>
                <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '2px' }}>
                  Potential: {f.potential} · {f.risk} risk
                </div>
              </div>
              <div style={{ textAlign: 'right' }}>
                <div style={{ fontSize: '16px', fontWeight: '700', color: barColor }}>{f.score}</div>
                <div style={{ fontSize: '10px', color: 'var(--text-muted)' }}>score</div>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}

function DistributionBar({ data, title }) {
  const total = Object.values(data).reduce((a, b) => a + b, 0) || 1;
  const items = [
    { label: 'Strong', key: 'strong', color: '#10b981', bg: 'rgba(16,185,129,0.15)' },
    { label: 'Moderate', key: 'moderate', color: '#6366f1', bg: 'rgba(99,102,241,0.15)' },
    { label: 'Weak', key: 'weak', color: '#f59e0b', bg: 'rgba(245,158,11,0.15)' },
  ];

  return (
    <div>
      <div style={{ fontSize: '13px', fontWeight: '600', color: 'var(--text-secondary)', marginBottom: '10px' }}>{title}</div>
      <div style={{ display: 'flex', gap: '4px', borderRadius: 'var(--radius-full)', overflow: 'hidden', height: '8px', marginBottom: '10px' }}>
        {items.map(item => {
          const pct = Math.round((data[item.key] || 0) / total * 100);
          return pct > 0 ? (
            <div key={item.key} style={{ flex: pct, background: item.color, transition: 'flex 0.6s ease' }} />
          ) : null;
        })}
      </div>
      <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
        {items.map(item => (
          <div key={item.key} style={{ display: 'flex', alignItems: 'center', gap: '5px', fontSize: '12px' }}>
            <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: item.color }} />
            <span style={{ color: 'var(--text-muted)' }}>{item.label}:</span>
            <span style={{ color: item.color, fontWeight: '600' }}>{data[item.key] || 0}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function ExecutiveOverview({ stats, loading }) {
  if (loading) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
        <div className="grid-4">
          {[1, 2, 3, 4].map(i => (
            <div key={i} className="skeleton" style={{ height: '120px' }} />
          ))}
        </div>
      </div>
    );
  }

  const topCandidate = stats?.top_candidate;
  const funnel = stats?.hiring_funnel || [];
  const scoreDistribution = stats?.score_distribution || {};
  const riskDistribution = stats?.risk_distribution || {};

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Stat Cards */}
      <div className="grid-4">
        <StatCard
          icon="👥"
          label="Total Candidates"
          value={stats?.total_candidates ?? 0}
          iconBg="rgba(99,102,241,0.15)"
        />
        <StatCard
          icon="🏆"
          label="Ranking Sessions"
          value={stats?.total_rankings ?? 0}
          iconBg="rgba(16,185,129,0.15)"
        />
        <StatCard
          icon="📊"
          label="Avg Final Score"
          value={stats?.avg_final_score != null ? `${stats.avg_final_score}` : '—'}
          iconBg="rgba(139,92,246,0.15)"
        />
        <StatCard
          icon="🚀"
          label="Avg Potential Score"
          value={stats?.avg_potential_score != null ? `${stats.avg_potential_score}` : '—'}
          iconBg="rgba(6,182,212,0.15)"
          trend="up"
          trendLabel="High growth detected"
        />
      </div>

      {/* Top Candidate + Funnel */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.4fr', gap: '16px' }}>
        {/* Top Candidate Spotlight */}
        <div className="card" style={{
          background: 'linear-gradient(135deg, rgba(99,102,241,0.1) 0%, rgba(139,92,246,0.1) 100%)',
          borderColor: 'var(--border-default)',
        }}>
          <div style={{ fontSize: '11px', color: 'var(--brand-primary)', textTransform: 'uppercase', letterSpacing: '0.08em', fontWeight: '600', marginBottom: '12px' }}>
            🏆 Top Candidate
          </div>
          {topCandidate ? (
            <>
              <div style={{ fontSize: '22px', fontWeight: '800', color: 'var(--text-primary)', marginBottom: '8px', letterSpacing: '-0.02em' }}>
                {topCandidate.name}
              </div>
              <div style={{ display: 'flex', gap: '20px', marginBottom: '16px', flexWrap: 'wrap' }}>
                <div>
                  <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Final Score</div>
                  <div style={{ fontSize: '24px', fontWeight: '700', color: 'var(--brand-success)' }}>{topCandidate.score}</div>
                </div>
                <div>
                  <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Potential</div>
                  <div style={{ fontSize: '24px', fontWeight: '700', color: 'var(--brand-primary)' }}>{topCandidate.potential_score}</div>
                </div>
              </div>
              <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                <span style={{
                  padding: '5px 12px', borderRadius: '999px',
                  background: 'rgba(16,185,129,0.15)', border: '1px solid rgba(16,185,129,0.3)',
                  color: 'var(--brand-success)', fontSize: '12px', fontWeight: '600',
                }}>
                  {topCandidate.recommendation}
                </span>
                <span style={{
                  padding: '5px 12px', borderRadius: '999px',
                  background: 'var(--bg-elevated)', border: '1px solid var(--border-subtle)',
                  color: 'var(--text-muted)', fontSize: '12px',
                }}>
                  {topCandidate.risk_level} risk
                </span>
              </div>
            </>
          ) : (
            <div style={{ color: 'var(--text-muted)', fontSize: '14px' }}>
              No ranking data yet. Submit a job description to rank candidates.
            </div>
          )}
        </div>

        {/* Distributions */}
        <div className="card">
          <div style={{ fontSize: '14px', fontWeight: '600', color: 'var(--text-primary)', marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            📈 Ranking Distributions
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            <DistributionBar data={scoreDistribution} title="Recommendation Distribution" />
            <div style={{ height: '1px', background: 'var(--border-subtle)' }} />
            <div>
              <div style={{ fontSize: '13px', fontWeight: '600', color: 'var(--text-secondary)', marginBottom: '10px' }}>Risk Distribution</div>
              <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
                {[
                  { label: 'Low', key: 'low', color: 'var(--brand-success)', bg: 'rgba(16,185,129,0.12)' },
                  { label: 'Medium', key: 'medium', color: 'var(--brand-warning)', bg: 'rgba(245,158,11,0.12)' },
                  { label: 'High', key: 'high', color: 'var(--brand-danger)', bg: 'rgba(239,68,68,0.12)' },
                ].map(item => (
                  <div key={item.key} style={{
                    flex: 1, padding: '12px', background: item.bg,
                    borderRadius: 'var(--radius-md)', textAlign: 'center',
                    border: `1px solid ${item.color}30`,
                  }}>
                    <div style={{ fontSize: '20px', fontWeight: '700', color: item.color }}>
                      {riskDistribution[item.key] || 0}
                    </div>
                    <div style={{ fontSize: '11px', color: item.color, fontWeight: '500' }}>{item.label}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Hiring Funnel */}
      <div className="card">
        <div className="section-header">
          <div>
            <div className="section-title">🔽 Hiring Funnel — Top Candidates</div>
            <div className="section-subtitle">Ranked by AI consensus score with potential and risk overlay</div>
          </div>
        </div>
        <HiringFunnel funnel={funnel} />
      </div>
    </div>
  );
}
