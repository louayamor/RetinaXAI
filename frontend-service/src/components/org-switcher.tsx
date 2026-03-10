'use client';

import { SidebarMenu, SidebarMenuButton, SidebarMenuItem } from '@/components/ui/sidebar';
import { Icons } from '@/components/icons';

export function OrgSwitcher() {
  return (
    <SidebarMenu>
      <SidebarMenuItem>
        <SidebarMenuButton size='lg' className='pointer-events-none'>
          <div className='bg-sidebar-primary text-sidebar-primary-foreground flex aspect-square size-8 shrink-0 items-center justify-center rounded-lg'>
            <Icons.logo className='size-4' />
          </div>
          <div className='grid flex-1 text-left text-sm leading-tight'>
            <span className='truncate font-semibold'>RetinaXAI</span>
            <span className='text-sidebar-foreground/60 truncate text-xs'>Clinical Platform</span>
          </div>
        </SidebarMenuButton>
      </SidebarMenuItem>
    </SidebarMenu>
  );
}