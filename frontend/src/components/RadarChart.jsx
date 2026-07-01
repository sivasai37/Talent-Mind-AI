// RadarChart.jsx — Candidate vs Job Radar Chart (SVG-based, no external deps)

export default function RadarChart({ candidate }) {
  if (!candidate) return null;

  const skills = candidate.skill_score || 0;
  const experience = candidate.experience_score || 0;
  const behavior = candidate.recruitability_score || 0;
  const potential = candidate.potential_score || 0;
  const semantic = candidate.semantic_score || 0;

  const axes = [
    { label: 'Skills', value: skills, color: '#6366f1' },
    { label: 'Experience', value: experience, color: '#8b5cf6' },
    { label: 'Behavior', value: behavior, color: '#06b6d4' },
    { label: 'Potential', value: potential, color: '#10b981' },
    { label: 'Role Fit', value: semantic, color: '#f59e0b' },
  ];

  const n = axes.length;
  const cx = 150;
  const cy = 150;
  const r = 110;
  const levels = 5;

  const angleStep = (2 * Math.PI) / n;
  const getCoords = (idx, radius) => {
    const angle = idx * angleStep - Math.PI / 2;
    return {
      x: cx + radius * Math.cos(angle),
      y: cy + radius * Math.sin(angle),
    };
  };

  // Grid levels
  const gridPolygons = Array.from({ length: levels }, (_, i) => {
    const ratio = (i + 1) / levels;
    return Array.from({ length: n }, (_, j) => {
      const p = getCoords(j, r * ratio);
      return `${p.x},${p.y}`;
    }).join(' ');
  });

  // Data polygon
  const dataPoints = axes.map((axis, i) => {
    const ratio = axis.value / 100;
    return getCoords(i, r * ratio);
  });

  const dataPolygon = dataPoints.map(p => `${p.x},${p.y}`).join(' ');

  // Axis endpoints
  const axisEndpoints = Array.from({ length: n }, (_, i) => getCoords(i, r));

  // Label positions (slightly outside)
  const labelPositions = Array.from({ length: n }, (_, i) => {
    const p = getCoords(i, r + 28);
    return { ...p, label: axes[i].label, value: axes[i].value, color: axes[i].color };
  });

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '16px' }}>
      <svg
        viewBox="0 0 300 300"
        width="300"
        height="300"
        style={{ overflow: 'visible' }}
      >
        {/* Background grid */}
        {gridPolygons.map((pts, i) => (
          <polygon
            key={i}
            points={pts}
            fill="none"
            stroke="rgba(99,102,241,0.12)"
            strokeWidth="1"
          />
        ))}

        {/* Axis lines */}
        {axisEndpoints.map((ep, i) => (
          <line
            key={i}
            x1={cx}
            y1={cy}
            x2={ep.x}
            y2={ep.y}
            stroke="rgba(99,102,241,0.2)"
            strokeWidth="1"
          />
        ))}

        {/* Data polygon */}
        <polygon
          points={dataPolygon}
          fill="rgba(99,102,241,0.15)"
          stroke="#6366f1"
          strokeWidth="2.5"
        />

        {/* Data points */}
        {dataPoints.map((p, i) => (
          <circle
            key={i}
            cx={p.x}
            cy={p.y}
            r="5"
            fill={axes[i].color}
            stroke={axes[i].color}
            strokeWidth="2"
          />
        ))}

        {/* Center */}
        <circle cx={cx} cy={cy} r="3" fill="rgba(99,102,241,0.4)" />

        {/* Labels */}
        {labelPositions.map((lp, i) => (
          <g key={i}>
            <text
              x={lp.x}
              y={lp.y - 3}
              textAnchor="middle"
              dominantBaseline="middle"
              fontSize="11"
              fontWeight="600"
              fill={lp.color}
              fontFamily="Inter, sans-serif"
            >
              {lp.label}
            </text>
            <text
              x={lp.x}
              y={lp.y + 11}
              textAnchor="middle"
              dominantBaseline="middle"
              fontSize="10"
              fill="rgba(148,163,184,0.8)"
              fontFamily="Inter, sans-serif"
            >
              {Math.round(lp.value)}%
            </text>
          </g>
        ))}
      </svg>

      {/* Legend */}
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '12px', justifyContent: 'center' }}>
        {axes.map((axis, i) => (
          <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px', color: 'var(--text-secondary)' }}>
            <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: axis.color, flexShrink: 0 }} />
            <span>{axis.label}: <strong style={{ color: axis.color }}>{Math.round(axis.value)}</strong></span>
          </div>
        ))}
      </div>
    </div>
  );
}
