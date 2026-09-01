import { Link } from "react-router-dom";
import { IconBox } from "./Icon";

export default function EmptyState({ icon, title, description, actionLabel, actionTo, onAction }) {
  const Icon = icon || IconBox;
  return (
    <div className="empty-state-card">
      <div className="empty-state-icon">
        <Icon size={36} />
      </div>
      <h3>{title}</h3>
      {description && <p>{description}</p>}
      {actionTo ? (
        <Link to={actionTo} className="btn btn-primary" style={{ marginTop: 12 }}>
          {actionLabel}
        </Link>
      ) : onAction ? (
        <button className="btn btn-primary" onClick={onAction} style={{ marginTop: 12 }}>
          {actionLabel}
        </button>
      ) : null}
    </div>
  );
}
