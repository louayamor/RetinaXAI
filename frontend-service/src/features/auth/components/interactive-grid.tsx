'use client';

export function InteractiveGrid() {
  return (
    <div className='absolute inset-0 overflow-hidden'>
      <div
        className='absolute inset-0 opacity-20'
        style={{
          backgroundImage:
            'linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)',
          backgroundSize: '44px 44px'
        }}
      />
      <div
        className='absolute inset-0'
        style={{
          background:
            'radial-gradient(ellipse 80% 60% at 50% 0%, rgba(45,212,191,0.08) 0%, transparent 70%)'
        }}
      />
    </div>
  );
}