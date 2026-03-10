import { getAccessToken } from '@/lib/auth';

export default function ProfileViewPage() {
  return (
    <div className='flex w-full flex-col gap-6 p-4'>
      <h2 className='text-xl font-semibold'>Profile</h2>
      <p className='text-muted-foreground text-sm'>
        Manage your account settings.
      </p>
    </div>
  );
}