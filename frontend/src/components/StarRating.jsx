import { IconStar } from "./dashboard/Icon";

/**
 * Renders a 0–5 star rating with an optional count.
 * `value` is the average (0–5). `count` is the number of reviews.
 * `size` is the star size in pixels (default 14).
 *
 * Examples:
 *   <StarRating value={4.3} count={87} />
 *   <StarRating value={0} />                // "No reviews yet"
 *   <StarRating value={5} count={1} size={18} />
 */
export default function StarRating({ value = 0, count = 0, size = 14 }) {
  const avg = Math.max(0, Math.min(5, Number(value) || 0));
  const full = Math.floor(avg);
  const half = avg - full >= 0.5;
  const empty = 5 - full - (half ? 1 : 0);

  if (!count) {
    return (
      <span className="star-rating star-rating-empty" aria-label="No reviews yet">
        {[0, 1, 2, 3, 4].map((i) => (
          <IconStar key={i} size={size} className="star star-empty" />
        ))}
        <span className="star-rating-count">No reviews yet</span>
      </span>
    );
  }

  return (
    <span
      className="star-rating"
      role="img"
      aria-label={`${avg.toFixed(1)} out of 5 stars from ${count} review${count === 1 ? "" : "s"}`}
    >
      {Array.from({ length: full }).map((_, i) => (
        <IconStar key={`f${i}`} size={size} className="star star-full" />
      ))}
      {half && <IconStar size={size} className="star star-half" />}
      {Array.from({ length: empty }).map((_, i) => (
        <IconStar key={`e${i}`} size={size} className="star star-empty" />
      ))}
      <span className="star-rating-value">{avg.toFixed(1)}</span>
      <span className="star-rating-count">({count})</span>
    </span>
  );
}
