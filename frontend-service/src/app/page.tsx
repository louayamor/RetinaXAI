'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { motion, useReducedMotion } from 'motion/react';
import { Button } from '@/components/ui/button';
import { fadeInUp, slideInUp, staggerContainer, staggerItem, buttonTap } from '@/lib/animations';
import Image from 'next/image';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const features = [
  {
    title: 'AI-Assisted Grading',
    description: 'EfficientNet-B3 powered diabetic retinopathy detection with explainable predictions',
    icon: '🔬',
  },
  {
    title: 'OCT Report Analysis',
    description: 'OCR-powered extraction from clinical reports for comprehensive patient data',
    icon: '📄',
  },
  {
    title: 'Clinical Reporting',
    description: 'LLM-generated reports with RAG for accurate clinical documentation',
    icon: '📊',
  },
];

export default function LandingPage() {
  const shouldReduceMotion = useReducedMotion();
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const res = await fetch(`${API_URL}/api/v1/auth/me`, {
          credentials: 'include',
        });
        if (res.ok) {
          window.location.href = '/dashboard/overview';
          return;
        }
      } catch {}
      setChecking(false);
    };
    checkAuth();
  }, []);

  if (checking) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[var(--brand-teal)]" />
      </div>
    );
  }

  return (
    <div className="min-h-screen w-full">
      <motion.div
        variants={shouldReduceMotion ? {} : fadeInUp}
        initial="hidden"
        animate="visible"
        className="flex flex-col"
      >
        {/* Hero Section */}
        <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
          {/* Background */}
          <div className="absolute inset-0 bg-gradient-to-b from-[#0a2e3e] via-[#0d3a4c] to-[#0a2e3e]" />
          
          {/* Decorative elements */}
          <div className="absolute -top-32 -right-32 h-96 w-96 rounded-full bg-[var(--brand-teal)]/10 blur-3xl" />
          <div className="absolute -bottom-32 -left-32 h-96 w-96 rounded-full bg-[var(--brand-gold)]/10 blur-3xl" />
          
          {/* Background image with overlay */}
          <div className="absolute inset-0 opacity-20">
            <Image
              src="https://images.unsplash.com/photo-1576091160550-2173dba999ef?w=1920&q=80"
              alt="Medical Technology"
              fill
              className="object-cover"
              unoptimized
            />
          </div>

          {/* Content */}
          <div className="relative z-10 container mx-auto px-4 text-center">
            <motion.div
              variants={shouldReduceMotion ? {} : staggerContainer}
              initial="hidden"
              animate="visible"
            >
              {/* Logo and Tagline */}
              <motion.div variants={shouldReduceMotion ? {} : staggerItem} className="mb-6">
                <h1 className="text-5xl md:text-7xl font-bold tracking-tight">
                  <span className="text-white">Retina</span>
                  <span className="text-[var(--brand-teal)]">X</span>
                  <span className="text-white">AI</span>
                </h1>
                <p className="mt-4 text-xl md:text-2xl text-white/80 max-w-2xl mx-auto">
                  AI-assisted retinal grading with explainable predictions for every diagnosis
                </p>
              </motion.div>

              {/* tagline */}
              <motion.div variants={shouldReduceMotion ? {} : staggerItem} className="mb-10">
                <p className="text-lg text-[var(--brand-teal)] font-medium">
                  Samaya Specialized Center • Clinical Decision Support
                </p>
              </motion.div>

              {/* CTA Buttons */}
              <motion.div
                variants={shouldReduceMotion ? {} : staggerItem}
                className="flex justify-center"
              >
                <motion.div variants={shouldReduceMotion ? {} : buttonTap}>
                  <a href="https://www.samayahospital.ae/home/" target="_blank" rel="noopener noreferrer">
                    <Button size="lg" className="text-lg px-8 py-6">
                      Visit our website
                    </Button>
                  </a>
                </motion.div>
              </motion.div>
            </motion.div>
          </div>

          {/* Scroll indicator */}
          <motion.div
            variants={shouldReduceMotion ? {} : slideInUp}
            initial="hidden"
            animate="visible"
            className="absolute bottom-8 left-1/2 -translate-x-1/2"
          >
            <div className="flex flex-col items-center text-white/50">
              <span className="text-sm mb-2">Scroll to explore</span>
              <motion.div
                animate={{ y: [0, 8, 0] }}
                transition={{ duration: 1.5, repeat: Infinity }}
                className="w-6 h-10 border-2 border-white/30 rounded-full flex justify-center pt-2"
              >
                <div className="w-1.5 h-3 bg-white/50 rounded-full" />
              </motion.div>
            </div>
          </motion.div>
        </section>

        {/* Features Section */}
        <section className="py-24 bg-background">
          <div className="container mx-auto px-4">
            <motion.div
              variants={shouldReduceMotion ? {} : staggerContainer}
              initial="hidden"
              animate="visible"
              className="text-center mb-16"
            >
              <motion.h2 variants={shouldReduceMotion ? {} : staggerItem} className="text-3xl md:text-4xl font-bold">
                Comprehensive <span className="text-[var(--brand-teal)]">Retinal</span> Healthcare
              </motion.h2>
              <motion.p variants={shouldReduceMotion ? {} : staggerItem} className="mt-4 text-lg text-muted-foreground max-w-2xl mx-auto">
                Three powerful features working together to assist clinicians in diabetic retinopathy detection and reporting
              </motion.p>
            </motion.div>

            {/* Feature Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {features.map((feature, index) => (
                <motion.div
                  key={feature.title}
                  variants={shouldReduceMotion ? {} : staggerItem}
                  className="relative group"
                >
                  <div className="absolute inset-0 bg-gradient-to-b from-[var(--brand-teal)]/10 to-transparent rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                  <div className="relative p-8 rounded-2xl border border-border bg-card hover:shadow-xl transition-shadow duration-300">
                    <div className="text-4xl mb-4">{feature.icon}</div>
                    <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
                    <p className="text-muted-foreground">{feature.description}</p>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* Footer CTA Section */}
        <section className="py-24 bg-gradient-to-b from-background to-muted">
          <div className="container mx-auto px-4 text-center">
            <motion.div
              variants={shouldReduceMotion ? {} : staggerContainer}
              initial="hidden"
              animate="visible"
            >
              <motion.div variants={shouldReduceMotion ? {} : staggerItem}>
                <h2 className="text-3xl md:text-4xl font-bold mb-4">
                  Ready to Transform Your Practice?
                </h2>
                <p className="text-lg text-muted-foreground mb-8 max-w-xl mx-auto">
                  Join clinical professionals using RetinaXAI for accurate diabetic retinopathy detection
                </p>
              </motion.div>
              <motion.div variants={shouldReduceMotion ? {} : staggerItem} className="flex justify-center gap-4">
                <Link href="/auth/register">
                  <Button size="lg" className="text-lg px-8">
                    Create Account
                  </Button>
                </Link>
                <Link href="/auth/login">
                  <Button size="lg" variant="outline" className="text-lg px-8">
                    Sign In
                  </Button>
                </Link>
              </motion.div>
            </motion.div>
          </div>
        </section>

        {/* Footer */}
        <footer className="py-8 border-t">
          <div className="container mx-auto px-4 flex flex-col md:flex-row justify-between items-center gap-4">
            <p className="text-sm text-muted-foreground">
              © 2024 RetinaXAI • Samaya Specialized Center
            </p>
            <p className="text-sm text-[var(--brand-teal)]">
              Clinical Decision Support System
            </p>
          </div>
        </footer>
      </motion.div>
    </div>
  );
}