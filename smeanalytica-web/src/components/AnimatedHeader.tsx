import { motion } from 'framer-motion';
import { ReactNode } from 'react';

interface AnimatedHeaderProps {
  children: ReactNode;
  subtitle?: string;
}

export function AnimatedHeader({ children, subtitle }: AnimatedHeaderProps) {
  return (
    <motion.header 
      className="py-16 px-4 text-center"
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
    >
      <h1 className="animated-header">
        {children}
      </h1>
      {subtitle && (
        <p className="mt-4 text-xl text-gray-600 dark:text-gray-400">
          {subtitle}
        </p>
      )}
    </motion.header>
  );
}
