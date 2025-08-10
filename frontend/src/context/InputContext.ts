import {FilePondFile} from 'filepond';
import React, {createContext} from 'react';

type InputContextType = {
  urlInputs: string[],
  setUrlInputs: React.Dispatch<React.SetStateAction<string[]>>,
  fileInputs: FilePondFile[],
  setFileInputs: React.Dispatch<React.SetStateAction<FilePondFile[]>>,
}

const InputContextState = {
  urlInputs: [],
  setUrlInputs: () => undefined,
  fileInputs: [],
  setFileInputs: () => undefined,
}

const InputContext = createContext<InputContextType>(InputContextState);

export default InputContext;