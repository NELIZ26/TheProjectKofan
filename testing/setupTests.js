import { afterEach, beforeAll, vi } from 'vitest';
import { config } from '@vue/test-utils';

config.global.stubs = {
  'font-awesome-icon': true,
};

beforeAll(() => {
  Object.defineProperty(window, 'matchMedia', {
    writable: true,
    value: vi.fn().mockImplementation((query) => ({
      matches: false,
      media: query,
      onchange: null,
      addListener: vi.fn(),
      removeListener: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    })),
  });

  global.ResizeObserver = class {
    observe() {}
    unobserve() {}
    disconnect() {}
  };

  document.documentElement.style.setProperty('--k-apple', '#8BCF5B');
  document.documentElement.style.setProperty('--k-forest', '#0f3b2a');
  document.documentElement.style.setProperty('--k-sky', '#3498db');
});

afterEach(() => {
  document.body.innerHTML = '';
});
