import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { BentoCard } from './BentoCard';

// Mock framer-motion to avoid animation-related issues in tests
vi.mock('framer-motion', () => ({
  motion: {
    div: ({ children, className }: { children: React.ReactNode; className?: string }) => (
      <div className={className}>{children}</div>
    ),
  },
}));

describe('BentoCard', () => {
  it('renders title and content correctly', () => {
    render(
      <BentoCard title="Test Title">
        <p>Test content</p>
      </BentoCard>
    );

    expect(screen.getByText('Test Title')).toBeInTheDocument();
    expect(screen.getByText('Test content')).toBeInTheDocument();
  });

  it('applies custom className', () => {
    render(
      <BentoCard title="Test" className="custom-class">
        <p>Content</p>
      </BentoCard>
    );

    const card = screen.getByRole('heading', { name: 'Test' }).parentElement;
    expect(card).toHaveClass('bento-card', 'custom-class');
  });
});
