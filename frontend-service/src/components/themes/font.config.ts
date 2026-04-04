import { Jost } from 'next/font/google';

const jost = Jost({
  subsets: ['latin'],
  variable: '--font-sans',
  weight: ['300', '400', '500', '600', '700', '800']
});

export const fontVariables = jost.variable;
