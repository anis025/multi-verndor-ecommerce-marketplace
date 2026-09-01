export default function ErrorMessage({ message, onRetry }) {
  return (
    <div className="error-container">
      <p className="error-message">{message || "Something went wrong."}</p>
      {onRetry && (
        <button className="btn btn-primary" onClick={onRetry}>
          Try Again
        </button>
      )}
    </div>
  );
}
