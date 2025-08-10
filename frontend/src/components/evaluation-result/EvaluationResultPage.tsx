import {ExpandMoreOutlined} from "@mui/icons-material";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import LinkIcon from '@mui/icons-material/Link';
import ShareIcon from '@mui/icons-material/Share';
import {CircularProgress} from "@mui/material";
import {Accordion, AccordionDetails, AccordionSummary, Box, Button, Divider, Grid, Link, Tooltip, Typography} from "@mui/material";
import React, {ReactElement, useEffect,useState} from 'react';
import {useLocation, useNavigate} from "react-router-dom";

import {useEvaluationResults, useInputData, useMetrics} from "../../client/queries";
import Container from '../../shared/container/Container';
import Header from "../../shared/header/Header";
import {EvaluationResultContentWrap} from "../../shared/wrappers/ElementWrap";
import {MetricType, ReferenceType} from "../../types/MetricType";
import ResultTable from "./ResultTable";
import ResultUrlLogic from "./ResultUrlLogic";

export default function EvaluationResultPage(): ReactElement {
  const {data: metrics, isLoading: isMetricsLoading} = useMetrics();
  const metricsInformation: MetricType[] | undefined = metrics?.metrics;

  const [naturalSize, setNaturalSize] = useState({ width: 0, height: 0 });
  const handleImageLoad = (event) => {
    const { naturalWidth, naturalHeight } = event.target;
    setNaturalSize({ width: naturalWidth, height: naturalHeight });
  };

  const navigate = useNavigate();
  const location = useLocation();
  const { pathname } = location;
  const id = pathname.split("/").at(-1);
  const [isWuiHidden, setIsWuiHidden] = useState(false);
  const {data: inputData, isLoading: isInputDataLoading} = useInputData(id);
  const {data: evaluationResults, refetch} = useEvaluationResults(id);
  const [isUrlCopied, setIsUrlCopied] = useState(false);
  const renderedWidth = naturalSize.width > 500 ? 500 : naturalSize.width;
  const renderedHeight = Math.round(naturalSize.height / (naturalSize.width / renderedWidth));

  useEffect(() => {
    let intervalId: number;
    if (evaluationResults && inputData && evaluationResults.length !== inputData.metrics_to_evaluate.length) {
      // Setup an interval to refetch data every 3000ms
      intervalId = setInterval(() => {
        refetch();
      }, 3000);
    }
    return () => clearInterval(intervalId);
  }, [evaluationResults, inputData, refetch]);


  const copyUrlToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(window.location.href);
      setIsUrlCopied(true);
      setTimeout(() => {
        setIsUrlCopied(false);
      }, 2000);
      // Optionally, show a notification to the user that the URL was copied successfully
    } catch (err) {
      console.error('Failed to copy: ', err);
      // Optionally, show an error notification to the user
    }
  }

  const shareUrlViaEmail = () => {
    const subject = encodeURIComponent(`URL for Evaluation result`);
    const body = encodeURIComponent(`${window.location.href}`);
    window.location.href = `mailto:?subject=${subject}&body=${body}`;
  };

  if((isInputDataLoading || isMetricsLoading)) return (
      <Grid direction="column" container justifyContent='center' alignItems='center'>
        <Grid>
          <Typography>
            Loading, please wait...
          </Typography>
        </Grid>
        <Grid>
          <CircularProgress />
        </Grid>
      </Grid>
  );

  if ((!inputData || !evaluationResults) && !isInputDataLoading) return (
    <Box>
      <Typography>
        Are you sure this is a correct URL? It seems like no evaluation result is stored here!
      </Typography>
      <Link href={'/'}>
        <Button>
          Go back to the homepage!
        </Button>
      </Link>
    </Box>
  );

  return (
    <Container>
        <Header>
          <Header.Container>
            <Header.Box gap='4px'>
              <Header.Title title={'Evaluation Result'} />
              <Header.Description
                description={
                  <Grid container>
                    <Button
                      onClick={() => navigate("/")}
                      variant="contained"
                      startIcon={<ArrowBackIcon />}
                      color='inherit'
                      size='small'
                      sx={{textTransform: 'initial'}}
                    >
                      Start New Evaluation
                    </Button>
                  </Grid>
                }
              />
            </Header.Box>
            <Header.Box>
              <Grid container>
                {
                  isUrlCopied ?
                    <Typography variant="body2">
                      URL copied to clipboard!
                    </Typography> :
                    <Button
                      startIcon={<LinkIcon />}
                      color='inherit'
                      size='small'
                      onClick={copyUrlToClipboard}
                      sx={{mr: '1rem'}}
                    >
                      Copy URL to clipboard
                    </Button>
                }
                <Button
                  startIcon={<ShareIcon />}
                  color='inherit'
                  size='small'
                  onClick={shareUrlViaEmail}
                >
                  Share URL via Email
                </Button>
              </Grid>
            </Header.Box>
          </Header.Container>
        </Header>
        <EvaluationResultContentWrap>
          {
            id === 'result' ?
              <ResultUrlLogic /> :
              <Grid container direction='column' spacing={2}>
                <Grid item>
                  <Typography component="h4" variant="h6" gutterBottom>
                    Selected metric(s) for evaluation
                  </Typography>
                  {
                    inputData?.metrics_to_evaluate.map((m: string) => (
                      <Box key={inputData.wui_name + "_" + m} display="flex">
                        <Typography>
                          {metricsInformation && metricsInformation[m].name} —
                        </Typography>
                        <Typography
                          style={{
                            marginLeft: 8,
                            color: evaluationResults?.some(obj => obj.metric_id === m) ? 'green' : 'inherit'
                          }}
                        >
                          {
                            evaluationResults?.some(obj => obj.metric_id === m) ?
                            'Result(s) ready!' : 'Still computing...'
                          }
                        </Typography>
                      </Box>

                    ))
                  }
                </Grid>
                <Divider sx={{mt: '1rem'}}/>
                <Grid item>
                  <Typography component="h4" variant="h6" gutterBottom>
                    WUI Preview
                  </Typography>
                  <Typography gutterBottom>
                    Intrinsic size: {naturalSize.width}x{naturalSize.height}px, rendered size: {renderedWidth}x{renderedHeight}px
                  </Typography>
                </Grid>
                <Grid item>
                  <Button variant="contained" onClick={() => setIsWuiHidden(!isWuiHidden)}>
                    {isWuiHidden ? 'Display WUI' : 'Hide WUI'}
                  </Button>
                </Grid>
                {
                  !isWuiHidden &&
                  <Grid item alignSelf='center'>
                    <Link href={inputData?.screenshot_url} target="_blank">
                      <img
                        alt={`wui_input${inputData?.screenshot_url}`}
                        src={inputData?.screenshot_url}
                        onLoad={handleImageLoad}
                        height={renderedHeight}
                        width={renderedWidth}
                      />
                    </Link>
                  </Grid>
                }
                <Divider sx={{mt: '1rem'}}/>
                <Grid item>
                  <Typography component="h4" variant="h6" gutterBottom>
                    Results
                  </Typography>
                </Grid>
                {
                  evaluationResults.map((value, index) => (
                    <Accordion key={`${value.metric_id}_${index}`} defaultExpanded>
                      <AccordionSummary
                        expandIcon={<ExpandMoreOutlined />}
                        aria-controls={`${value.metric_id}_${index}__content`}
                      >
                        {metricsInformation[value.metric_id]['name']}
                      </AccordionSummary>
                      <AccordionDetails>
                        <Typography variant="body2" gutterBottom>
                          {metricsInformation[value.metric_id]['description']}
                        </Typography>
                        <Typography variant="body2" gutterBottom>
                          References: {
                          metricsInformation[value.metric_id]['references'].reduce(
                            (acc: ReactElement, v: ReferenceType, idx: number) => {
                            const isLast = idx === metricsInformation[value.metric_id]['references'].length - 1;
                            const link =
                              <Tooltip key={`${value.metric_id}_${v.title}`} describeChild title={v.title}>
                                <Link href={v.url} rel="noreferrer" target="_blank">
                                  {`[${idx + 1}]`}
                                </Link>
                              </Tooltip>
                            if (isLast) {
                              return [...acc, link];
                            } else {
                              return [...acc, link, ', '];
                            }
                          }, [])
                        }
                        </Typography>
                        <ResultTable metricInformation={metricsInformation[value.metric_id]} results={value} />
                      </AccordionDetails>
                    </Accordion>
                  ))
                }
              </Grid>
          }
        </EvaluationResultContentWrap>
    </Container>
  );
}