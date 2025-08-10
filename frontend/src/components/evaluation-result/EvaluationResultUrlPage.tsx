import { useMetrics } from "../../client/queries";
import { MetricType } from "../../types/MetricType";
import {CircularProgress, Grid, Typography} from "@mui/material";
import React, {ReactElement} from "react";

import Container from "../../shared/container/Container";
import Header from "../../shared/header/Header";
import {EvaluationResultContentWrap} from "../../shared/wrappers/ElementWrap";
import MetricInformation from "../wui-metrics-input/MetricInformation";
import ResultUrlLogic from "./ResultUrlLogic";

export default function EvaluationResultPage(): ReactElement {
    const {data: metrics, isLoading: isMetricsLoading} = useMetrics();
    const metricsInformation: MetricType[] | undefined = metrics?.metrics;

    if((isMetricsLoading)) return (
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

  return (
      <Grid container direction='column'>
          <Container>
              <Header>
                  <Header.Container>
                      <Header.Box gap='4px'>
                          <Header.Title title={'Evaluation Results Access Link(s)'} />
                          <Header.Description description={`Note: Do not refresh this page as the application state will not persist!`}/>
                      </Header.Box>
                  </Header.Container>
              </Header>
              <EvaluationResultContentWrap>
                  <Typography
                      variant="body1"
                      sx={{mb: '2rem'}}
                  >
                      The table below provides links to the evaluation results for each WUI input.
                      New entries will appear in the table as soon as they become available.
                  </Typography>
                  <ResultUrlLogic />
              </EvaluationResultContentWrap>
          </Container>
          <Container>
              <MetricInformation metrics={metricsInformation}/>
          </Container>
      </Grid>
  );
}