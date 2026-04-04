import { Metadata } from 'next';
import { redirect } from 'next/navigation';

export const metadata: Metadata = {
  title: 'RetinaXAI Auth',
  robots: { index: false, follow: false }
};

export default function AuthPage() {
  redirect('/auth/login');
}
