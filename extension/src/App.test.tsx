import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import App from './App';
import '@testing-library/jest-dom';

// Mock chrome extension API
vi.stubGlobal('chrome', {
  tabs: {
    query: vi.fn().mockResolvedValue([{ id: 1, url: 'https://dataverse-social.com', title: 'Dataverse Terms' }]),
    sendMessage: vi.fn().mockResolvedValue({ success: true, text: 'Mocked policy text', title: 'Test', url: 'https://dataverse-social.com' }),
  },
  scripting: {
    executeScript: vi.fn().mockResolvedValue([]),
  }
});

describe('SmartConsent App', () => {
  it('renders without crashing', () => {
    render(<App />);
    expect(screen.getByText('SmartConsent')).toBeInTheDocument();
  });

  it('renders settings when gear icon is clicked', () => {
    render(<App />);
    const settingsButton = screen.getByTitle('Privacy Preferences');
    fireEvent.click(settingsButton);
    expect(screen.getByText('Privacy Preferences')).toBeInTheDocument();
  });

  it('shows analyze button initially', () => {
    render(<App />);
    expect(screen.getByRole('button', { name: /Analyze Active Tab/i })).toBeInTheDocument();
  });
});

