import { IconCheck } from "./Icon";

const STEPS = [
  { key: "pending", label: "Placed" },
  { key: "confirmed", label: "Confirmed" },
  { key: "processing", label: "Processing" },
  { key: "shipped", label: "Shipped" },
  { key: "out_for_delivery", label: "Out for Delivery" },
  { key: "delivered", label: "Delivered" },
];

const STATUS_INDEX = Object.fromEntries(STEPS.map((s, i) => [s.key, i]));

export default function ProgressTimeline({ status }) {
  const idx = STATUS_INDEX[status] ?? 0;
  const isCancelled = status === "cancelled";

  if (isCancelled) {
    return (
      <div className="timeline timeline-cancelled">
        <div className="timeline-cancelled-badge">Order Cancelled</div>
      </div>
    );
  }

  return (
    <div className="timeline" role="list" aria-label="Order progress">
      {STEPS.map((step, i) => {
        const state = i < idx ? "done" : i === idx ? "current" : "todo";
        return (
          <div key={step.key} className={`timeline-step timeline-${state}`} role="listitem">
            <div className="timeline-dot">
              {state === "done" ? <IconCheck size={14} /> : <span>{i + 1}</span>}
            </div>
            <div className="timeline-label">{step.label}</div>
            {i < STEPS.length - 1 && <div className="timeline-line" />}
          </div>
        );
      })}
    </div>
  );
}
