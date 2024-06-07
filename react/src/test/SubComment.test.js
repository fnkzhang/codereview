import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom/extend-expect';
import SubComment from '../components/Comments/SubComment';

describe('SubComment', () => {
  it('renders the author and text', () => {
    render(<SubComment author="John Doe" text="This is a comment." />);

    const authorElement = screen.getByText('John Doe');
    const textElement = screen.getByText('This is a comment.');

    expect(authorElement).toBeInTheDocument();
    expect(authorElement).toHaveClass('Comment-author');
    expect(textElement).toBeInTheDocument();
    expect(textElement).toHaveClass('Comment-text');
  });
});