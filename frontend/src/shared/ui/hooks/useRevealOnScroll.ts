import { useEffect, useRef, useState } from "react";

export interface UseRevealOptions {
  threshold?: number;
  staggerMs?: number;
  index?: number;
}

export const useRevealOnScroll = <T extends HTMLElement = HTMLDivElement>({
  threshold = 0.15,
  staggerMs = 80,
  index = 0,
}: UseRevealOptions = {}) => {
  const ref = useRef<T | null>(null);
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;

    // Respect prefers-reduced-motion
    if (typeof window !== "undefined" && typeof window.matchMedia === "function" && window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      setIsVisible(true);
      return;
    }


    if (typeof window === "undefined" || typeof IntersectionObserver === "undefined") {
      setIsVisible(true);
      return;
    }

    const observer = new IntersectionObserver(

      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          observer.unobserve(entry.target);
        }
      },
      { threshold }
    );

    observer.observe(el);

    return () => {
      if (el) observer.unobserve(el);
    };
  }, [threshold]);

  const style: React.CSSProperties = {
    opacity: isVisible ? 1 : 0,
    transform: isVisible ? "translate3d(0, 0, 0)" : "translate3d(0, 32px, 0)",
    transition: `opacity 600ms cubic-bezier(0.16, 1, 0.3, 1) ${index * staggerMs}ms, transform 600ms cubic-bezier(0.16, 1, 0.3, 1) ${index * staggerMs}ms`,
    willChange: "opacity, transform",
  };

  return { ref, isVisible, style };
};
