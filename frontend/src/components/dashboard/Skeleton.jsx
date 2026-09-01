export function Skeleton({ width = "100%", height = 16, radius = 6, style = {} }) {
  return (
    <span
      className="skeleton"
      style={{ display: "inline-block", width, height, borderRadius: radius, ...style }}
    />
  );
}

export function SkeletonRow({ cols = 3 }) {
  return (
    <div className="skeleton-row">
      {Array.from({ length: cols }).map((_, i) => (
        <Skeleton key={i} height={20} />
      ))}
    </div>
  );
}

export function SkeletonCard({ height = 140 }) {
  return (
    <div className="skeleton-card" style={{ height }}>
      <Skeleton height={14} width="40%" style={{ marginBottom: 12 }} />
      <Skeleton height={28} width="60%" style={{ marginBottom: 8 }} />
      <Skeleton height={12} width="80%" />
    </div>
  );
}
