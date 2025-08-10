import {
  Alert,
  Box,
  CircularProgress,
  Button,
  LinearProgress,
  Link,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography
} from "@mui/material";
import React, {ReactElement, ReactNode, useContext, useEffect, useRef,useState} from "react";

import {useEvaluateFileInput, useEvaluateUrlInput} from "../../client/mutations";
import RequestsContext from "../../context/RequestsContext";
import {ResultMetadataType} from "../../context/ResultMetadataContext";
import ResultMetadataContext from "../../context/ResultMetadataContext";
import ShareIcon from "@mui/icons-material/Share";


function createData(
  result_id: string,
  wui_name: string,
  wui_type: "url" | "html" | "png",
) {
  return { result_id, wui_name, wui_type };
}

export default function ResultUrlLogic(): ReactElement {
  const {urlRequests, fileRequests, setUrlRequests, setFileRequests} = useContext(RequestsContext);
  const fetchInitiated = useRef(false);
  const [totalRequestsNumber] = useState(urlRequests.length + fileRequests.length);
  const [failedRequestsNumber, setFailedRequestNumber] = useState(0);
  const { resultMetadata, setResultMetadata } = useContext(ResultMetadataContext);
  const {mutateAsync: evaluateUrlInput} = useEvaluateUrlInput();
  const {mutateAsync: evaluateFileInput} = useEvaluateFileInput();

  useEffect(() => {
    async function fetchAndProcessRequests() {
      // Do nothing if fetch has already been initiated
      if (fetchInitiated.current) return;

      fetchInitiated.current = true; // Set the flag to true to avoid re-fetching

      const allRequests = [
        ...fileRequests.map(input => evaluateFileInput(input)),
        ...urlRequests.map(input => evaluateUrlInput(input))
      ];

      // Clear requests to avoid running them twice
      setUrlRequests([]);
      setFileRequests([]);

      // execute the requests
      allRequests.forEach((request) => {
        request.then((result: ResultMetadataType) => {
          // Update state with each successful result as it comes in
          setResultMetadata(prevResults => [...prevResults, result]);
        }).catch(error => {
          setFailedRequestNumber(failedRequestsNumber + 1);
          console.error(error);
        });
      });
    }

    if ((urlRequests.length > 0 || fileRequests.length > 0) && resultMetadata.length < totalRequestsNumber) {
      fetchAndProcessRequests().catch(console.error);
    }

  }, [urlRequests, fileRequests, totalRequestsNumber]);

  const rows = [];

  resultMetadata.forEach(v => {
    rows.push(createData(v.result_id, v.wui_name, v.wui_type));
  });

  const shareUrlsViaEmail = () => {
    const subject = encodeURIComponent(`WUI Evaluation results links`);
    const padRight = (str, length) => {
      return str + ' '.repeat(Math.max(0, length - str.length));
    };
    const wuiNameLength = 60;
    const wuiTypeLength = 15;
    let body = 'Here are the evaluation result links:\n\n';
    body += padRight('WUI Name', wuiNameLength) + padRight('WUI Type', wuiTypeLength) + 'Links\n';
    body += '-'.repeat(wuiNameLength + wuiTypeLength + 100) + '\n';

    resultMetadata.forEach((result) => {
      body += padRight(result.wui_name, wuiNameLength) + padRight(result.wui_type, wuiTypeLength) + `${window.location.href}/${result.result_id}\n`;
    });

    body = encodeURIComponent(body);
    window.location.href = `mailto:?subject=${subject}&body=${body}`;
  };

  return (
    <>
      <TableContainer component={Paper as ReactNode}>
        <Table aria-label="result URL table">
          <TableHead>
            <TableRow>
              <TableCell width="30%">WUI Name</TableCell>
              <TableCell width="25%">WUI Format Type</TableCell>
              <TableCell width="45%">Evaluation Results Link</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {rows && rows.map((row) => (
              <TableRow
                key={row.result_id}
              >
                <TableCell component="th" scope="row">
                  {row.wui_name}
                </TableCell>
                <TableCell>{(row.wui_type).toUpperCase()}</TableCell>
                <TableCell>
                  <Link href={`${window.location.href}/${row.result_id}`} rel="noreferrer" target="_blank">
                    {`${window.location.href}/${row.result_id}`}
                  </Link>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
      {
        resultMetadata.length < totalRequestsNumber &&
        <Box display="flex" alignItems="center" sx={{mt: '2rem'}}>
          <CircularProgress />
          <Typography variant="body2" color="textSecondary" sx={{ml: 2}}>
            Generating access links, please wait...
          </Typography>
        </Box>
      }
      <Box display="flex" alignItems="center" sx={{mt: '2rem'}}>
        <Box width="10%" mr={1}>
          <LinearProgress variant="determinate" value={resultMetadata.length/totalRequestsNumber * 100} />
        </Box>
        <Box minWidth={35}>
          <Typography variant="body2" color="textSecondary">
            {`${resultMetadata.length} / ${totalRequestsNumber}`} of evaluation result links ready.
          </Typography>
        </Box>
        {
          resultMetadata.length > 0 &&
          <Box ml='auto'>
            <Button
              startIcon={<ShareIcon />}
              color='inherit'
              size='small'
              onClick={shareUrlsViaEmail}
            >
              Share URL(s) via Email
            </Button>
          </Box>
        }
      </Box>
      {
        failedRequestsNumber > 0 &&
        <Box width="30%">
          <Alert severity='error'>
            Note: {failedRequestsNumber} request(s) failed!
          </Alert>
        </Box>
      }
    </>
  );
}