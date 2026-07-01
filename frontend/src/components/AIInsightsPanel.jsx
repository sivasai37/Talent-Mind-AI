// AIInsightsPanel.jsx — AI Talent Insights & Market Intelligence Panel

import { useState, useEffect } from 'react';
import { getTalentInsights } from '../api';

export default function AIInsightsPanel({ roleType = 'general', jobDescription = '' }) {
  const [insights, setInsights] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    let mounted = true;
    setLoading(true);
    getTalentInsights(jobDescription, roleType)
      .then(data => { if (mounted) setInsights(data); })
      .catch(() => {})
      .finally(() => { if (mounted) setLoading(false); });
    return () => { mounted = false; };
  }, [roleType]);

  const ROLE_ICONS = {
    backend: '⚙️', frontend: '🎨', leadership: '👥', research: '🔬',
    data: '📊', design: '🖌️', general: '💼',
  };

  if (loading) {
    return (
      <div className="card">
        <div className="skeleton" style={{ height: '20px', width: '40%', marginBottom: '16px' }} />
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {[1,2,3].map(i => <div key={i} className="skeleton" style={{ height: '60px' }} />)}
        </div>
      </div>
    );
  }

  if (!insights) return null;

  const sections = [
    {
      title: '📈 Market Insights',
      items: insights.market_insights || [],
      color: 'var(--brand-primary)',
      bg: 'rgba(99,102,241,0.08)',
      border: 'rgba(99,102,241,0.2)',
    },
    {
      title: '🔥 Skill Trends',
      items: insights.skill_trends || [],
      color: 'var(--brand-accent)',
      bg: 'rgba(6,182,212,0.08)',
      border: 'rgba(6,182,212,0.2)',
    },
    {
      title: '💡 Hiring Recommendations',
      items: insights.hiring_recommendations || [],
      color: 'var(--brand-success)',
      bg: 'rgba(16,185,129,0.08)',
      border: 'rgba(16,185,129,0.2)',
    },
  ];

  return (
    <div className="card">
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '20px' }}>
        <span style={{ fontSize: '24px' }}>{ROLE_ICONS[roleType] || '💼'}</span>
        <div>
          <div style={{ fontSize: '14px', fontWeight: '700', color: 'var(--text-primary)' }}>
            AI Talent Intelligence
          </div>
          <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
            {roleType.charAt(0).toUpperCase() + roleType.slice(1)} roles · Market & hiring insights
          </div>
        </div>
      </div>

      {/* Talent pool stats */}
      {insights.talent_pool_stats && (
        <div style={{
          display: 'flex', gap: '12px', marginBottom: '20px',
          padding: '12px', background: 'var(--bg-elevated)',
          borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)',
        }}>
          <div style={{ textAlign: 'center', flex: 1 }}>
            <div style={{ fontSize: '20px', fontWeight: '700', color: 'var(--brand-primary)' }}>
              {insights.talent_pool_stats.total_candidates_in_pool}
            </div>
            <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Candidates in Pool</div>
          </div>
          <div style={{ width: '1px', background: 'var(--border-subtle)' }} />
          <div style={{ textAlign: 'center', flex: 1 }}>
            <div style={{ fontSize: '20px', fontWeight: '700', color: 'var(--brand-success)' }}>
              {insights.talent_pool_stats.average_experience_years}
            </div>
            <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Avg Experience (yrs)</div>
          </div>
        </div>
      )}

      {sections.map((section, i) => (
        <div key={i} style={{ marginBottom: i < sections.length - 1 ? '16px' : 0 }}>
          <div style={{ fontSize: '12px', fontWeight: '700', color: section.color, marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
            {section.title}
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            {section.items.map((item, j) => (
              <div key={j} style={{
                padding: '10px 12px', background: section.bg,
                borderRadius: 'var(--radius-md)', border: `1px solid ${section.border}`,
                display: 'flex', alignItems: 'flex-start', gap: '8px',
              }}>
                <span style={{ color: section.color, fontSize: '12px', fontWeight: '700', flexShrink: 0, marginTop: '1px' }}>▸</span>
                <p style={{ fontSize: '12px', color: 'var(--text-secondary)', lineHeight: '1.5' }}>{item}</p>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
