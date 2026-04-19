export default function SkeletonCard({ lines = 3 }: { lines?: number }) {
  return (
    <div className="skeleton-card" aria-hidden="true">
      <div className="skeleton-line skeleton-line-title" />
      {Array.from({ length: lines }).map((_, index) => (
        <div key={index} className="skeleton-line" />
      ))}
    </div>
  );
}
