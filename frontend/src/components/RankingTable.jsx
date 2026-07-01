// RankingTable.jsx — Enterprise Candidate Ranking Table

function getRankBadgeClass(rank) {
  if (rank === 1) return 'rank-badge rank-1';
  if (rank === 2) return 'rank-badge rank-2';
  if (rank === 3) return 'rank-badge rank-3';
  return 'rank-badge rank-n';
}

function RiskDot({ level }) {
  const colors = { low: 'var(--brand-success)', medium: 'var(--brand-warning)', high: 'var(--brand-danger)' };
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
      <div style={{
        width: '7px', height: '7px', borderRadius: '50%',
        background: colors[level] || colors.medium, flexShrink: 0,
      }} />
      <span style={{ fontSize: '11px', color: colors[level] || colors.medium, fontWeight: '600', textTransform: 'capitalize' }}>
        {level || 'medium'}
      </span>
    </div>
  );
}

function RecommendationPill({ rec }) {
  const r = (rec || '').toLowerCase();
  const isStrong = r.includes('strong');
  const isWeak = r.includes('weak');
  return (
    <span style={{
      fontSize: '10px', fontWeight: '700', padding: '3px 8px',
      borderRadius: '999px', textTransform: 'uppercase', letterSpacing: '0.04em',
      background: isStrong ? 'rgba(16,185,129,0.12)' : isWeak ? 'rgba(239,68,68,0.12)' : 'rgba(245,158,11,0.12)',
      color: isStrong ? 'var(--brand-success)' : isWeak ? 'var(--brand-danger)' : 'var(--brand-warning)',
      border: `1px solid ${isStrong ? 'rgba(16,185,129,0.3)' : isWeak ? 'rgba(239,68,68,0.3)' : 'rgba(245,158,11,0.3)'}`,
    }}>
      {rec || 'Moderate'}
    </span>
  );
}

function ScoreBar({ value, color = '#6366f1' }) {
  const pct = Math.min(100, Math.max(0, value || 0));
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
      <div style={{ flex: 1, height: '4px', background: 'var(--border-subtle)', borderRadius: '999px', overflow: 'hidden' }}>
        <div style={{
          height: '100%', width: `${pct}%`,
          background: color, borderRadius: '999px',
          transition: 'width 0.6s ease',
        }} />
      </div>
      <span style={{ fontSize: '11px', color: 'var(--text-muted)', width: '26px', textAlign: 'right', fontWeight: '600' }}>
        {Math.round(pct)}
      </span>
    </div>
  );
}

export default function RankingTable({ rankings, onSelect, selectedId }) {
  if (!rankings || !rankings.length) {
    return (
      <div className="empty-state" style={{ padding: '40px 20px' }}>
        <div className="empty-state-icon">📋</div>
        <div className="empty-state-title">No Rankings Yet</div>
        <div className="empty-state-desc">
          Submit a job description above to rank candidates using HireGenius AI.
        </div>
      </div>
    );
  }

  return (
    <div style={{ overflowX: 'auto' }}>
      <table className="data-table">
        <thead>
          <tr>
            <th style={{ width: '44px' }}>#</th>
            <th>Candidate</th>
            <th style={{ width: '140px' }}>Final Score</th>
            <th style={{ width: '80px' }}>Potential</th>
            <th style={{ width: '90px' }}>Risk</th>
            <th style={{ width: '110px' }}>Recommendation</th>
          </tr>
        </thead>
        <tbody>
          {rankings.map((row, index) => {
            const candidateId = row.candidate?.id || row.candidate_id;
            const isSelected = candidateId === selectedId;
            const rank = row.rank || (index + 1);
            const recommendation = row.recruiter_recommendation ||
              row.payload?.recruiter_ai?.recommendation ||
              row.payload?.final_recommendation || 'Moderate Fit';
            const riskLevel = row.risk_level || 'medium';
            const potentialScore = Math.round(row.potential_score || 0);
            const finalScore = Math.round(row.final_score || 0);

            const getScoreColor = (s) => s >= 75 ? '#10b981' : s >= 50 ? '#6366f1' : '#f59e0b';

            return (
              <tr
                key={candidateId || index}
                onClick={() => onSelect(row)}
                className={isSelected ? 'active' : ''}
                style={{ cursor: 'pointer' }}
              >
                <td>
                  <div className={getRankBadgeClass(rank)}>{rank}</div>
                </td>
                <td>
                  <div style={{ fontWeight: '600', color: 'var(--text-primary)', fontSize: '14px', marginBottom: '2px' }}>
                    {row.candidate?.full_name || 'Unknown'}
                  </div>
                  <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                    {row.candidate?.years_experience || 0} yrs · {
                      row.candidate?.skills
                        ? row.candidate.skills.split(',').slice(0, 2).join(', ')
                        : 'No skills listed'
                    }
                  </div>
                </td>
                <td>
                  <div style={{ marginBottom: '4px' }}>
                    <span style={{ fontSize: '18px', fontWeight: '700', color: getScoreColor(finalScore) }}>
                      {finalScore}
                    </span>
                    <span style={{ fontSize: '11px', color: 'var(--text-muted)', marginLeft: '2px' }}>/100</span>
                  </div>
                  <ScoreBar value={finalScore} color={getScoreColor(finalScore)} />
                </td>
                <td>
                  <div style={{ textAlign: 'center' }}>
                    <span style={{ fontSize: '15px', fontWeight: '700', color: 'var(--brand-primary)' }}>
                      {potentialScore}
                    </span>
                  </div>
                </td>
                <td>
                  <RiskDot level={riskLevel} />
                </td>
                <td>
                  <RecommendationPill rec={recommendation} />
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
