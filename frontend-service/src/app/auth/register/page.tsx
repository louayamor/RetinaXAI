import { Metadata } from 'next';
import SignUpView from '@/features/auth/components/sign-up-view';

export const metadata: Metadata = {
  title: 'RetinaXAI Register',
  robots: { index: false, follow: false }
};

export default function RegisterPage() {
  return <SignUpView />;
}
