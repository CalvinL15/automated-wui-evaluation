import Grid from "@mui/material/Grid";
import React, {ReactElement} from "react";

import Container from "../../shared/container/Container";
import Header from "../../shared/header/Header";
import {MetricExtensionWrap} from "../../shared/wrappers/ElementWrap";
import MetricExtensionGuide from "./MetricExtensionGuide";
import FileUploader from "./MetricExtensionInputReceiver";

export default function MetricExtensionPage(): ReactElement {
  return (
    <Grid minWidth={'100%'}>
      <Container>
        <Header>
          <Header.Container>
            <Header.Box gap='4px'>
              <Header.Title title={'Metric Extension Interface'} />
              <Header.Description
                description={'Upload the necessary files for requesting metric extension here!'}
              />
            </Header.Box>
          </Header.Container>
        </Header>
        <MetricExtensionWrap>
          <Grid container direction="column">
            <FileUploader />
          </Grid>
        </MetricExtensionWrap>
      </Container>
      <Container>
        <MetricExtensionGuide />
      </Container>
    </Grid>
  )
}