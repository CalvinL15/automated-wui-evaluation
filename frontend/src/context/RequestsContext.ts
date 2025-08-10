import React, {createContext} from 'react';

import {FileInputRequestType,UrlInputRequestType} from "../types/RequestType";

type RequestsContextType = {
  urlRequests: UrlInputRequestType[];
  fileRequests: FileInputRequestType[];
  setUrlRequests: React.Dispatch<React.SetStateAction<UrlInputRequestType[]>>;
  setFileRequests: React.Dispatch<React.SetStateAction<FileInputRequestType[]>>;
}

const RequestContextState = {
  urlRequests: [],
  fileRequests: [],
  setUrlRequests:  () => undefined,
  setFileRequests: () => undefined
}

const RequestsContext = createContext<RequestsContextType>(RequestContextState);

export default RequestsContext;