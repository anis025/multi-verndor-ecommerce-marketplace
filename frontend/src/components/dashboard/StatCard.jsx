export default function StatCard({ icon: Icon, label, value, tone = "default" }) {
  return (
    <div className={`stat-card stat-card-${tone}`}>
      <div className="stat-card-icon">
        <Icon size={22} />
      </div>
      <div>
        <div className="stat-card-label">{label}</div>
        <div className="stat-card-value">{value}</div>
      </div>
    </div>
  );
}
