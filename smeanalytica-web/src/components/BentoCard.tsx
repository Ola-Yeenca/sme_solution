import { motion } from 'framer-motion';
import { ReactNode } from 'react';

interface BentoCardProps {
  title: string;
  children: ReactNode;
  className?: string;
  delay?: number;
}

export function BentoCard({ title, children, className = '', delay = 0 }: BentoCardProps) {
  return (
    <motion.div 
      className={`bento-card ${className}`}
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5, delay }}
    >
      <h2 className="text-2xl font-semibold mb-4">{title}</h2>
      {children}
    </motion.div>
  );
}
