"use client";

import { useState, useEffect, useRef } from "react";

interface AnimatedCounterProps {
  end: number;
  duration?: number;
  suffix?: string;
  prefix?: string;
  decimals?: number;
  label: string;
  format?: (value: number) => string;
}

export function AnimatedCounter({
  end,
  duration = 2000,
  suffix = "",
  prefix = "",
  decimals = 0,
  label,
  format,
}: AnimatedCounterProps) {
  const [count, setCount] = useState(0);
  const [isVisible, setIsVisible] = useState(false);
  const [hasAnimated, setHasAnimated] = useState(false);
  const elementRef = useRef<HTMLDivElement>(null);

  const defaultFormat = (value: number): string => {
    let formatted = value.toFixed(decimals);
    if (decimals === 0) {
      formatted = parseInt(formatted).toLocaleString("es-AR");
    } else {
      formatted = parseFloat(formatted).toLocaleString("es-AR", {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals,
      });
    }
    return `${prefix}${formatted}${suffix}`;
  };

  const formatter = format || defaultFormat;

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting && !hasAnimated) {
            setIsVisible(true);
          }
        });
      },
      { threshold: 0.3, rootMargin: "0px 0px -50px 0px" }
    );

    if (elementRef.current) {
      observer.observe(elementRef.current);
    }

    return () => {
      if (elementRef.current) {
        observer.unobserve(elementRef.current);
      }
    };
  }, [hasAnimated]);

  useEffect(() => {
    if (!isVisible || hasAnimated) return;

    let startTime: number;
    let animationId: number;

    const updateCounter = (timestamp: number) => {
      if (!startTime) startTime = timestamp;
      const progress = Math.min((timestamp - startTime) / duration, 1);

      const easeOutQuart = 1 - Math.pow(1 - progress, 4);
      const currentValue = end * easeOutQuart;

      setCount(currentValue);

      if (progress < 1) {
        animationId = requestAnimationFrame(updateCounter);
      } else {
        setCount(end);
        setHasAnimated(true);
      }
    };

    animationId = requestAnimationFrame(updateCounter);

    return () => {
      if (animationId) {
        cancelAnimationFrame(animationId);
      }
    };
  }, [isVisible, end, duration, hasAnimated]);

  return (
    <div ref={elementRef} className="text-center">
      <div className="stat-value">{formatter(count)}</div>
      <div className="stat-label">{label}</div>
    </div>
  );
}