import { Metadata } from 'next';
import SignInView from '@/features/auth/components/sign-in-view';

export const metadata: Metadata = {
  title: 'RetinaXAI Sign In',
  robots: { index: false, follow: false }
};

export default function LoginPage() {
  return <SignInView />;
}
