import React from 'react';
import { render } from '@testing-library/react';
import App from './App';

test('Test', () => {
  const { getByText } = render(<App />);
  const headerElement = getByText(/Allekirjoitusten tunnistaja/i);
  expect(headerElement).toBeInTheDocument();
});
