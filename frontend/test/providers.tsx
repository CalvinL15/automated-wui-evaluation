import {QueryClient, QueryClientProvider} from '@tanstack/react-query';
import React, {FC, ReactNode} from 'react';

const getTestQueryClient = () =>
  new QueryClient({
    defaultOptions: {queries: {retry: false}}
  });
export const getTestQueryClientProvider =
  (client = getTestQueryClient()): FC<{children?: ReactNode}> =>
  ({children}) => <QueryClientProvider client={client}>{children}</QueryClientProvider>;
