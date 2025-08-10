import React, {createContext} from 'react';

export interface ResultMetadataType {
  wui_name: string;
  wui_type: 'url' | 'html' | 'png';
  result_id: string;
}


type ResultMetadataContextType = {
  resultMetadata: ResultMetadataType[],
  setResultMetadata: React.Dispatch<React.SetStateAction<ResultMetadataType[]>>,
}

const ResultMetadataContextState = {
  resultMetadata: [],
  setResultMetadata: () => undefined,
}

const ResultMetadataContext = createContext<ResultMetadataContextType>(ResultMetadataContextState);

export default ResultMetadataContext;