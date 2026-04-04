import Link from 'next/link';
import UserAuthForm from './user-auth-form';

export default function SignUpView() {
  return (
    <div className='relative h-screen flex-col items-center justify-center md:grid lg:max-w-none lg:grid-cols-2 lg:px-0'>
      <div className='relative hidden h-full flex-col bg-muted p-10 text-white lg:flex dark:border-r'>
        <div className='absolute inset-0'>
          <img
            src='https://images.unsplash.com/photo-1551076805-e1869033e561?w=1200&q=80'
            alt='RetinaXAI Technology'
            className='h-full w-full object-cover opacity-30'
          />
          <div className='absolute inset-0 bg-gradient-to-t from-[#0a2e3e] via-[#0a2e3e]/80 to-transparent' />
        </div>
        <div className='relative z-20 flex items-center text-lg font-medium'>
          <img
            src='https://www.samayahospital.ae/home/images/logo.png'
            alt='Samaya Specialized Center'
            className='mr-3 h-8 w-auto'
          />
          <span className='text-[#20bdbe]'>RetinaXAI</span>
        </div>
        <div className='relative z-20 mt-auto'>
          <blockquote className='space-y-2'>
            <p className='text-lg'>
              &ldquo;Join the clinical frontier. Start running explainable DR
              predictions in minutes.&rdquo;
            </p>
            <footer className='text-sm text-[#20bdbe]/80'>
              Doctor Registration
            </footer>
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
              className='underline underline-offset-4 hover:text-[#20bdbe]'
            >
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
