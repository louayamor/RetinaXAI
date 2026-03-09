import Link from 'next/link';
import UserAuthForm from './user-auth-form';
import { InteractiveGrid } from './interactive-grid';

export default function SignUpView() {
  return (
    <div className='relative h-screen flex-col items-center justify-center md:grid lg:max-w-none lg:grid-cols-2 lg:px-0'>
      <div className='relative hidden h-full flex-col bg-muted p-10 text-white lg:flex dark:border-r'>
        <div className='absolute inset-0 bg-zinc-900' />
        <InteractiveGrid />
        <div className='relative z-20 flex items-center text-lg font-medium'>
          <svg
            xmlns='http://www.w3.org/2000/svg'
            viewBox='0 0 24 24'
            fill='none'
            stroke='currentColor'
            strokeWidth='2'
            strokeLinecap='round'
            strokeLinejoin='round'
            className='mr-2 h-6 w-6'
          >
            <circle cx='12' cy='12' r='10' />
            <circle cx='12' cy='12' r='4' />
            <line x1='12' y1='2' x2='12' y2='6' />
            <line x1='12' y1='18' x2='12' y2='22' />
            <line x1='2' y1='12' x2='6' y2='12' />
            <line x1='18' y1='12' x2='22' y2='12' />
          </svg>
          RetinaXAI
        </div>
        <div className='relative z-20 mt-auto'>
          <blockquote className='space-y-2'>
            <p className='text-lg'>
              &ldquo;Join the clinical frontier. Start running explainable DR
              predictions in minutes.&rdquo;
            </p>
            <footer className='text-sm'>Doctor Registration</footer>
          </blockquote>
        </div>
      </div>
      <div className='flex h-full items-center p-4 lg:p-8'>
        <div className='mx-auto flex w-full flex-col justify-center space-y-6 sm:w-[350px]'>
          <div className='flex flex-col space-y-2 text-center'>
            <h1 className='text-2xl font-semibold tracking-tight'>
              Create an account
            </h1>
            <p className='text-sm text-muted-foreground'>
              Register as a clinician to manage patients and run predictions
            </p>
          </div>
          <UserAuthForm mode='register' />
          <p className='px-8 text-center text-sm text-muted-foreground'>
            Already have an account?{' '}
            <Link
              href='/auth/login'
              className='underline underline-offset-4 hover:text-primary'
            >
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}