'use client';

import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Search, X } from 'lucide-react';

type FilterStatus = 'all' | 'completed' | 'pending' | 'running' | 'failed';

interface ReportFiltersProps {
  search: string;
  onSearchChange: (value: string) => void;
  status: FilterStatus;
  onStatusChange: (status: FilterStatus) => void;
}

const STATUS_OPTIONS: { value: FilterStatus; label: string }[] = [
  { value: 'all', label: 'All' },
  { value: 'completed', label: 'Completed' },
  { value: 'pending', label: 'Pending' },
  { value: 'running', label: 'Running' },
  { value: 'failed', label: 'Failed' },
];

export function ReportFilters({ search, onSearchChange, status, onStatusChange }: ReportFiltersProps) {
  return (
    <div className="flex flex-col md:flex-row gap-4 items-start md:items-center justify-between">
      {/* Status Pills */}
      <div className="flex flex-wrap gap-2">
        {STATUS_OPTIONS.map((option) => (
          <Button
            key={option.value}
            variant={status === option.value ? 'default' : 'outline'}
            size="sm"
            onClick={() => onStatusChange(option.value)}
            className={`${
              status === option.value 
                ? 'bg-[var(--brand-teal)] hover:bg-[#1a9a9a]' 
                : 'hover:bg-muted'
            }`}
          >
            {option.label}
          </Button>
        ))}
      </div>

      {/* Search */}
      <div className="relative w-full md:w-64">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          placeholder="Search by patient..."
          value={search}
          onChange={(e) => onSearchChange(e.target.value)}
          className="pl-9"
        />
        {search && (
          <button
            onClick={() => onSearchChange('')}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
          >
            <X className="h-4 w-4" />
          </button>
        )}
      </div>
    </div>
  );
}