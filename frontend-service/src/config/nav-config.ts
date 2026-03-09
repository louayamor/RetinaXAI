import { NavItem } from '@/types';

export const navItems: NavItem[] = [
  {
    title: 'Overview',
    url: '/dashboard/overview',
    icon: 'dashboard',
    isActive: false,
    shortcut: ['o', 'o'],
    items: []
  },
  {
    title: 'Patients',
    url: '/dashboard/patients',
    icon: 'user',
    isActive: false,
    shortcut: ['p', 'p'],
    items: []
  },
  {
    title: 'Predictions',
    url: '/dashboard/predictions',
    icon: 'media',
    isActive: false,
    shortcut: ['r', 'r'],
    items: []
  },
  {
    title: 'Reports',
    url: '/dashboard/reports',
    icon: 'post',
    isActive: false,
    shortcut: ['e', 'e'],
    items: []
  },
  {
    title: 'Monitoring',
    url: '/dashboard/monitoring',
    icon: 'billing',
    isActive: false,
    shortcut: ['m', 'm'],
    items: []
  },
  {
    title: 'Account',
    url: '#',
    icon: 'account',
    isActive: true,
    items: [
      {
        title: 'Profile',
        url: '/dashboard/profile',
        icon: 'profile',
        shortcut: ['u', 'u']
      }
    ]
  }
];