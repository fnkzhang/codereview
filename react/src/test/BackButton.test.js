import React from 'react';
import { render, fireEvent } from '@testing-library/react';
import { useNavigate } from 'react-router-dom';
import BackButton from '../components/Buttons/BackButton';

jest.mock('react-router-dom', () => ({
  useNavigate: jest.fn(),
}));

describe('BackButton', () => {
  it('navigates to the specified location when clicked', () => {
    const navigate = jest.fn();
    useNavigate.mockReturnValue(navigate);

    const location = '/some-location';

    const { getByText } = render(<BackButton location={location} />);

    const button = getByText('Return');

    fireEvent.click(button);

    expect(navigate).toHaveBeenCalledWith(location);
  });
});