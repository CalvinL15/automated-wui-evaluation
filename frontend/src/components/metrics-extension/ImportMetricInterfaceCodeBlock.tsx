import {Grid} from "@mui/material";
import React from "react";
import { a11yLight,CodeBlock } from "react-code-blocks";

export default function ImportMetricInterfaceCodeBlock() {
  const code = `from metrics_evaluator.metrics.metric_interface import MetricInterface`
  return (
    <Grid marginTop='1rem' marginBottom='2rem'>
      <CodeBlock
        text={code}
        language='python'
        showLineNumbers={false}
        theme={a11yLight}
      />
    </Grid>
  );
}