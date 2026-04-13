'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import SignInView from '@/features/auth/components/sign-in-view';
import { isAuthenticated } from '@/lib/auth';

export default function LoginPage() {
  const router = useRouter();

  useEffect(() => {
    if (isAuthenticated()) {
      router.replace('/dashboard/overview');
    }
  }, [router]);

  return <SignInView />;
}
