import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import {Button, CircularProgress} from "@mui/material";
import Grid from '@mui/material/Grid';
import React, {ReactElement, useContext, useState} from 'react';

import InputContext from "../../context/InputContext";
import Container from '../../shared/container/Container';
import Header from "../../shared/header/Header";
import Typography from "../../shared/typography/Typography";
import {ButtonWrap, WUIInputWrap} from "../../shared/wrappers/ElementWrap";
import {useMetrics} from "../../client/queries";
import FileUploader from './FileUploader';
import MetricInformation from './MetricInformation';
import MetricSelection from "./MetricSelection";
import URLInput from "./URLInput";

export default function MainInterfacePage(): ReactElement {
  const { urlInputs, fileInputs } = useContext(InputContext);
  const [isFirstStepCompleted, setIsFirstStepCompleted] = useState(false);
  const {data: wrappedMetrics, isLoading: isMetricsLoading} = useMetrics();
  const metrics = wrappedMetrics?.metrics;

  if (isMetricsLoading) {
      return (
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
      )
  }

  return (
    <Grid container direction='column'>
      <Container>
        <Header>
          <Header.Container>
            <Header.Box gap='4px'>
              <Header.Title title={!isFirstStepCompleted ? 'First Step: Provide your Web User Interface (WUI) Inputs!' : 'Second Step: Select Metrics to Evaluate.'} />
              <Header.Description
                description={!isFirstStepCompleted ?
                  'Accepted input types: URL, PNG, HTML, or ZIP (with index.html inside, do not use relative paths!)' :
                  <Button
                    onClick={()=>setIsFirstStepCompleted(false)}
                    startIcon={<ArrowBackIcon />}
                    color='inherit'
                    size='small'
                    sx={{textTransform: 'initial'}}
                  >
                    Go back to the first step. Note: All selected metrics will be cleared!
                  </Button>
                }
              />
            </Header.Box>
          </Header.Container>
        </Header>
        {
          !isFirstStepCompleted ?
            (
              <WUIInputWrap>
                <Grid container direction='column'>
                  <URLInput />
                  <Grid item alignSelf='center'>
                    <Typography> AND/OR </Typography>
                  </Grid>
                  <FileUploader />
                  <Grid item alignSelf='self-end'>
                    <ButtonWrap>
                      <Button
                        color='primary'
                        variant="contained"
                        disabled={urlInputs.length === 0 && fileInputs.length === 0}
                        onClick={() => setIsFirstStepCompleted(true)}
                      >
                        Confirm WUI input(s)
                      </Button>
                    </ButtonWrap>
                  </Grid>
                  <Grid item>
                    <Typography>
                      For information regarding the the available metrics, please refer to the metrics information section provided below!
                    </Typography>
                  </Grid>
                </Grid>
              </WUIInputWrap>
            ) : ( <MetricSelection metrics={metrics}/> )
        }
      </Container>
      <Container>
        <MetricInformation metrics={metrics}/>
      </Container>
    </Grid>
  );
}