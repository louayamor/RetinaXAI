import React from 'react';
import Image from 'next/image';
import { SidebarTrigger } from '../ui/sidebar';
import { Separator } from '../ui/separator';
import { Breadcrumbs } from '../breadcrumbs';
import SearchInput from '../search-input';
import { UserNav } from './user-nav';
import { ConnectionStatus } from '@/components/layout/connection-status';

export default function Header() {
  return (
    <header className='flex h-24 shrink-0 items-center justify-between gap-4 transition-[width,height] ease-linear group-has-data-[collapsible=icon]/sidebar-wrapper:h-20'>
      <div className='flex items-center gap-4 px-8'>
        <SidebarTrigger className='-ml-1 h-10 w-10' />
        <Separator orientation='vertical' className='mr-4 h-6' />
        <Breadcrumbs />
      </div>

      <div className='flex items-center gap-4 px-8'>
        <div className='hidden md:flex'>
          <SearchInput />
        </div>
        <ConnectionStatus />
        <Image
          src='https://www.samayahospital.ae/home/images/logo.png'
          alt='Samaya Specialized Center'
          width={48}
          height={48}
          className='h-12 w-auto'
          unoptimized
        />
        <UserNav />
      </div>
    </header>
  );
}
