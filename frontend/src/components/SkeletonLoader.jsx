export function Skeleton({ className = '', lines = 1 }) {
  return (
    <div className={`skeleton-wrap ${className}`} aria-hidden="true">
      {Array.from({ length: lines }).map((_, i) => (
        <div key={i} className="skeleton-line" style={{ width: i === lines - 1 ? '72%' : '100%' }} />
      ))}
    </div>
  );
}

export function TableSkeleton({ rows = 6, cols = 5 }) {
  return (
    <div className="table-skeleton" aria-busy="true" aria-label="Loading rankings">
      <div className="table-skeleton-head">
        {Array.from({ length: cols }).map((_, i) => (
          <div key={i} className="skeleton-cell skeleton-shimmer" />
        ))}
      </div>
      {Array.from({ length: rows }).map((_, r) => (
        <div key={r} className="table-skeleton-row">
          {Array.from({ length: cols }).map((_, c) => (
            <div key={c} className="skeleton-cell skeleton-shimmer" />
          ))}
        </div>
      ))}
    </div>
  );
}

export default Skeleton;
