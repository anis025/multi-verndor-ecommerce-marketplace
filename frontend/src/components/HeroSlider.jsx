import { useState, useEffect, useCallback } from "react";
import { Link } from "react-router-dom";

const slides = [
  {
    image: "/images/hero-banner.png",
    fullImage: true,
  },
  {
    image: "/images/hero-banner-2.png",
    tag: "NEW ARRIVALS",
    title: "Discover the Latest Trends",
    subtitle: "Fresh styles and innovative products added daily from top sellers around the world.",
    primaryBtn: { text: "Browse New", to: "/?search=new" },
    secondaryBtn: { text: "View All Products", to: "/" },
  },
  {
    image: "/images/hero-banner-3.png",
    tag: "BEST DEALS",
    title: "Unbeatable Prices, Quality Guaranteed",
    subtitle: "Save big on thousands of products. Verified sellers, secure payments, fast delivery.",
    primaryBtn: { text: "Shop Deals", to: "/?search=sale" },
    secondaryBtn: { text: "Start Selling", to: "/register" },
  },
];

export default function HeroSlider() {
  const [current, setCurrent] = useState(0);
  const [isPaused, setIsPaused] = useState(false);

  const next = useCallback(() => {
    setCurrent((prev) => (prev + 1) % slides.length);
  }, []);

  const prev = useCallback(() => {
    setCurrent((prev) => (prev - 1 + slides.length) % slides.length);
  }, []);

  useEffect(() => {
    if (isPaused) return;
    const timer = setInterval(next, 5000);
    return () => clearInterval(timer);
  }, [isPaused, next]);

  const slide = slides[current];

  return (
    <section
      className="hero-slider"
      onMouseEnter={() => setIsPaused(true)}
      onMouseLeave={() => setIsPaused(false)}
    >
      <div className="hero-slider-inner">
        {slides.map((s, i) => (
          <div
            key={i}
            className={`hero-slide ${i === current ? "active" : ""} ${s.fullImage ? "hero-slide-full" : ""}`}
            style={{ backgroundImage: `url(${s.image})` }}
          />
        ))}

        {!slide.fullImage && <div className="hero-overlay" />}

        <button className="hero-arrow hero-arrow-left" onClick={prev} aria-label="Previous">
          &#8249;
        </button>
        <button className="hero-arrow hero-arrow-right" onClick={next} aria-label="Next">
          &#8250;
        </button>

        {!slide.fullImage && (
          <div className="hero-slide-content">
            <span className="hero-tag">{slide.tag}</span>
            <h1 className="hero-title">{slide.title}</h1>
            <p className="hero-subtitle">{slide.subtitle}</p>
            <div className="hero-buttons">
              <Link to={slide.primaryBtn.to} className="hero-btn hero-btn-primary">
                {slide.primaryBtn.text} <span className="hero-btn-arrow">&rarr;</span>
              </Link>
              {slide.secondaryBtn && (
                <Link to={slide.secondaryBtn.to} className="hero-btn hero-btn-secondary">
                  {slide.secondaryBtn.text}
                </Link>
              )}
            </div>
          </div>
        )}

        <div className="hero-dots">
          {slides.map((_, i) => (
            <button
              key={i}
              className={`hero-dot ${i === current ? "active" : ""}`}
              onClick={() => setCurrent(i)}
              aria-label={`Slide ${i + 1}`}
            />
          ))}
        </div>
      </div>
    </section>
  );
}
