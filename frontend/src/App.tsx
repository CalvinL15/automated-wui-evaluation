import styled from "@emotion/styled";
import {Button, Link} from "@mui/material";
import {FilePondFile} from "filepond";
import React, {useState} from 'react';
import {Navigate, Route, Routes} from 'react-router-dom';
import { useLocation } from 'react-router-dom';

import Logo from '/vsr_logo.png';
import EvaluationResultPage from './components/evaluation-result/EvaluationResultPage';
import EvaluationResultUrlPage from './components/evaluation-result/EvaluationResultUrlPage';
import MetricExtensionPage from "./components/metrics-extension/MetricExtensionPage";
import MainInterfacePage  from './components/wui-metrics-input/MainInterfacePage';
import InputContext from './context/InputContext';
import RequestsContext from "./context/RequestsContext";
import ResultMetadataContext, {ResultMetadataType} from './context/ResultMetadataContext';
import Header from './shared/header/Header';
import BodyWrap from "./shared/wrappers/BodyWrap";
import PageWrap from './shared/wrappers/PageWrap';
import {FileInputRequestType,UrlInputRequestType} from "./types/RequestType";

const HeaderWrap = styled.div`
  top: 0px;
  position: sticky;
  z-index: 2;
`;

const StyledLink = styled(Link)`
  color: black;
  text-decoration: none;
  font-size: 16px;
  @media (max-width: 1000px) {
    font-size: 12px;
  }
`

function App() {
  const location = useLocation();
  const [resultMetadata, setResultMetadata] = useState<ResultMetadataType[]>([]);
  const [urlInputs, setUrlInputs] = useState<string[]>([]);
  const [fileInputs, setFileInputs] = useState<FilePondFile[]>([]);

  const [urlRequests, setUrlRequests] = useState<UrlInputRequestType[]>([]);
  const [fileRequests, setFileRequests] = useState<FileInputRequestType[]>([]);


  return (
    <PageWrap>
      <HeaderWrap>
        <Header>
          <Header.Container alignItems="center">
            <Header.Area alignContent="start" alignItems="start">
              <Link href="/">
                <img width="48" height="48" style={{marginRight: '1.5rem'}} src={Logo} alt="vsr-logo" />
              </Link>
              <Header.Box gap={'4px'}>
                <Header.Title title="UIQLab" />
                <Header.Description description={'Evaluate your web user interfaces with empirically validated metrics!'} />
              </Header.Box>
            </Header.Area>
            <Header.Area alignContent="end" alignItems="end">
              <Button variant={"contained"} color={'inherit'}>
                {
                  !location.pathname.includes("/extension") ?
                    <StyledLink href="/extension"><b>Metric Extension Interface</b></StyledLink>
                    :
                    <StyledLink href="/"><b>WUI Evaluation Interface</b></StyledLink>
                }
              </Button>
            </Header.Area>
          </Header.Container>
        </Header>
      </HeaderWrap>
      <BodyWrap>
        <RequestsContext.Provider
          value={{
            urlRequests,
            setUrlRequests,
            fileRequests,
            setFileRequests
          }}
        >
          <ResultMetadataContext.Provider
            value={{
              resultMetadata,
              setResultMetadata
            }}
          >
            <InputContext.Provider
              value={{
                urlInputs,
                setUrlInputs,
                fileInputs,
                setFileInputs,
              }}
            >
              <Routes>
                <Route path="/" element={<MainInterfacePage />} />
                <Route path="/extension" element={<MetricExtensionPage />} />
                <Route path="/result" element={<EvaluationResultUrlPage />} />
                <Route path="/result/:id" element={<EvaluationResultPage />} />
                <Route path="*" element={<Navigate replace to="/" />} />
              </Routes>
            </InputContext.Provider>
          </ResultMetadataContext.Provider>
        </RequestsContext.Provider>
      </BodyWrap>
    </PageWrap>
  )
}

export default App;
