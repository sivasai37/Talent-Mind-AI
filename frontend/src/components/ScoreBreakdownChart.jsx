// ScoreBreakdownChart.jsx — Horizontal bar chart for score dimensions

export default function ScoreBreakdownChart({ data }) {
  if (!data || !data.length) return null;

  const getColor = (score) => {
    if (score >= 75) return 'var(--brand-success)';
    if (score >= 50) return 'var(--brand-primary)';
    if (score >= 30) return 'var(--brand-warning)';
    return 'var(--brand-danger)';
  };

  const getGradient = (score) => {
    if (score >= 75) return 'linear-gradient(90deg, #10b981, #06b6d4)';
    if (score >= 50) return 'linear-gradient(90deg, #6366f1, #8b5cf6)';
    if (score >= 30) return 'linear-gradient(90deg, #f59e0b, #f97316)';
    return 'linear-gradient(90deg, #ef4444, #dc2626)';
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', marginTop: '16px' }}>
      {data.map((item, i) => {
        const score = Math.round(item.score || 0);
        return (
          <div key={i}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
              <span style={{ fontSize: '13px', fontWeight: '500', color: 'var(--text-secondary)' }}>
                {item.name}
              </span>
              <span style={{ fontSize: '14px', fontWeight: '700', color: getColor(score) }}>
                {score}
              </span>
            </div>
            <div className="score-bar">
              <div
                className="score-bar-fill"
                style={{
                  width: `${Math.min(100, score)}%`,
                  background: getGradient(score),
                  transition: 'width 0.8s ease',
                }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}
