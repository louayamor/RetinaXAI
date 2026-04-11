import { type Variants } from 'motion';

const EASE_OUT_EXPO = [0.22, 1, 0.36, 1] as const;

export const fadeInUp: Variants = {
  hidden: { opacity: 0, y: 16 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.4, ease: EASE_OUT_EXPO }
  }
};

export const fadeIn: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { duration: 0.3, ease: EASE_OUT_EXPO }
  }
};

export const staggerContainer: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.05,
      delayChildren: 0.1
    }
  }
};

export const staggerItem: Variants = {
  hidden: { opacity: 0, y: 16 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.35, ease: EASE_OUT_EXPO }
  }
};

export const staggerItemFast: Variants = {
  hidden: { opacity: 0, y: 12 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.25, ease: EASE_OUT_EXPO }
  }
};

export const scaleIn: Variants = {
  hidden: { opacity: 0, scale: 0.95 },
  visible: {
    opacity: 1,
    scale: 1,
    transition: { duration: 0.25, ease: EASE_OUT_EXPO }
  }
};

export const slideInUp: Variants = {
  hidden: { opacity: 0, y: 24 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.35, ease: EASE_OUT_EXPO }
  }
};

export const slideInRight: Variants = {
  hidden: { opacity: 0, x: 24 },
  visible: {
    opacity: 1,
    x: 0,
    transition: { duration: 0.35, ease: EASE_OUT_EXPO }
  }
};

export const buttonTap: Variants = {
  rest: { scale: 1 },
  tap: { scale: 0.98, transition: { duration: 0.1, ease: 'easeOut' } }
};

export const rowHover: Variants = {
  rest: { backgroundColor: 'transparent' },
  hover: {
    backgroundColor: 'rgba(32, 189, 190, 0.05)',
    transition: { duration: 0.15 }
  }
};

export const inputFocus: Variants = {
  rest: { borderColor: 'var(--input)', boxShadow: 'none' },
  focus: {
    borderColor: 'var(--primary)',
    boxShadow: '0 0 0 2px rgba(32, 189, 190, 0.15)',
    transition: { duration: 0.2 }
  }
};

export const statusPulse: Variants = {
  rest: { opacity: 1 },
  pulse: {
    opacity: [1, 0.6, 1],
    transition: { duration: 2, repeat: Infinity, ease: 'easeInOut' }
  }
};

export const shimmer: Variants = {
  initial: { x: '-100%' },
  animate: {
    x: '200%',
    transition: { duration: 1.5, repeat: Infinity, ease: 'linear' }
  }
};

export const borderPulse: Variants = {
  rest: { borderColor: 'var(--border)' },
  hover: {
    borderColor: 'var(--primary)',
    transition: { duration: 0.3 }
  }
};

export const cardHover: Variants = {
  rest: { y: 0, boxShadow: 'none' },
  hover: {
    y: -2,
    boxShadow: 'var(--shadow-md)',
    transition: { duration: 0.2, ease: 'easeOut' }
  }
};

export const dialogOverlay: Variants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { duration: 0.2 } }
};

export const dialogContent: Variants = {
  hidden: { opacity: 0, scale: 0.96, y: 8 },
  visible: {
    opacity: 1,
    scale: 1,
    y: 0,
    transition: { duration: 0.25, ease: EASE_OUT_EXPO }
  }
};