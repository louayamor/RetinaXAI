'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import SignInView from '@/features/auth/components/sign-in-view';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function LoginPage() {
  const router = useRouter();
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    const checkAuth = async () => {
      try {
        await new Promise(resolve => setTimeout(resolve, 800));

        const res = await fetch(`${API_URL}/api/v1/auth/me`, {
          credentials: 'include',
        });

        if (res.ok) {
          router.replace('/dashboard/overview');
        }
      } catch {
        // Ignore errors, show login
      } finally {
        setChecking(false);
      }
    };

    checkAuth();
  }, [router]);

  if (checking) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#20bdbe]" />
      </div>
    );
  }

  return <SignInView />;
}
