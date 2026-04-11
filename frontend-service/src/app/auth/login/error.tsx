'use client';

import NextError from 'next/error';
import { useEffect } from 'react';

export default function AuthLoginError({
  error,
}: {
  error: Error & { digest?: string };
}) {
  useEffect(() => {
    console.error('Auth login error:', error);
  }, [error]);

  return (
    <html>
      <body>
        <NextError statusCode={0} title="Authentication Error" />
      </body>
    </html>
  );
}