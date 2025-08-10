import React, { ReactElement } from "react";

import Header from "../../shared/header/Header";
import Typography from "../../shared/typography/Typography";
import {MetricsInformationContentWrap} from "../../shared/wrappers/ElementWrap";
import {MetricType} from "../../types/MetricType";
import MetricTable from "./MetricTable";

interface MetricInformationType {
  metrics: MetricType[] | undefined;
}

export default function MetricInformation({metrics}: MetricInformationType): ReactElement {
  return (
    <>
      <Header>
        <Header.Container>
          <Header.Box gap='2px'>
            <Header.Title title={'Metrics Information'} />
          </Header.Box>
        </Header.Container>
      </Header>
      <MetricsInformationContentWrap>
        <Typography>
          The table below presents the metrics available for evaluation, detailing their names, descriptions, accepted input formats, as well as relevant references.
        </Typography>
        <MetricTable metrics={metrics}/>
      </MetricsInformationContentWrap>
    </>
  )
}