import react from '@vitejs/plugin-react-swc';
import { defineConfig as defineViteConfig, mergeConfig } from 'vite';
import { defineConfig as defineVitestConfig } from 'vitest/config';

const viteConfig = defineViteConfig({
  plugins: [react()],
  assetsInclude: ['**/*.md'],
  server: {
    port: 3000
  }
});

const vitestConfig = defineVitestConfig({
  test: {
    globals: true,
    environment: 'happy-dom',
    restoreMocks: true,
    coverage: {
      clean: true,
      reporter: ['lcov', 'json'],
      reportsDirectory: '../coverage'
    },
    root: './src',
    exclude: ['./src/test'],
    alias: {
      '\\.(css)$': 'identity-obj-proxy',
      '\\.(jpg|jpeg|png)$': './src/__mocks__/fileMock.ts',
    },
    testTimeout: 20000,
    setupFiles: ['./src/test/setupTests.ts'],
    server: {
      deps: {
        fallbackCJS: true
      }
    }
  }
});

export default mergeConfig(viteConfig, vitestConfig);