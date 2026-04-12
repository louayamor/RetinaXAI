'use client';

import { motion, useReducedMotion, type Variants } from 'motion/react';

interface SamayaLogoProps {
  className?: string;
  size?: 'sm' | 'md' | 'lg';
  animate?: boolean;
  variant?: 'full' | 'letters' | 'accent';
}

const sizeClasses = {
  sm: { text: 'text-2xl', letter: 'text-2xl', icon: 'w-6 h-6' },
  md: { text: 'text-4xl', letter: 'text-4xl', icon: 'w-8 h-8' },
  lg: { text: 'text-6xl', letter: 'text-6xl', icon: 'w-12 h-12' },
};

const letterVariants: Variants = {
  hidden: { opacity: 0, y: 20 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: {
      delay: i * 0.08,
      duration: 0.35,
      ease: 'easeOut',
    },
  }),
};

export function SamayaLogo({
  className = '',
  size = 'md',
  animate = true,
  variant = 'full',
}: SamayaLogoProps) {
  const shouldReduceMotion = useReducedMotion();
  const sizes = sizeClasses[size];
  const word = 'SAMAYA';

  const shouldAnimate = animate && !shouldReduceMotion;

  if (!shouldAnimate) {
    return (
      <span
        className={`${sizes.text} font-bold tracking-wider ${className}`}
        style={{
          color: variant === 'accent' ? 'var(--primary)' : undefined,
        }}
      >
        {word}
      </span>
    );
  }

  return (
    <motion.span
      className={`${sizes.text} font-bold tracking-wider inline-flex ${className}`}
      style={{
        color: variant === 'accent' ? 'var(--primary)' : undefined,
      }}
      initial="hidden"
      animate="visible"
      variants={{
        hidden: {},
        visible: {
          transition: {
            staggerChildren: 0.05,
            delayChildren: 0.1,
          },
        },
      }}
    >
      {word.split('').map((letter, i) => (
        <motion.span
          key={i}
          custom={i}
          variants={letterVariants}
          className="inline-block"
          style={{
            color: letter === 'A' && variant === 'full' ? 'var(--primary)' : undefined,
          }}
        >
          {letter}
        </motion.span>
      ))}
    </motion.span>
  );
}

interface SamayaWordmarkProps {
  className?: string;
  showBadge?: boolean;
}

export function SamayaWordmark({ className = '', showBadge = true }: SamayaWordmarkProps) {
  const shouldReduceMotion = useReducedMotion();

  return (
    <div className={`flex items-center gap-3 ${className}`}>
      <SamayaLogo size="sm" animate={!shouldReduceMotion} variant="accent" />
      {showBadge && (
        <span className="px-2 py-0.5 text-xs font-medium bg-[#20bdbe]/10 text-[#20bdbe] rounded-full">
          AI
        </span>
      )}
    </div>
  );
}