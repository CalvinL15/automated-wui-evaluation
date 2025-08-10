import {Grid, Link, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow } from "@mui/material";
import React, {ReactElement, ReactNode, useState} from "react";

import {EvaluationResultType} from "@/types/EvaluationResultType";
import {MetricType} from "@/types/MetricType";

import DownloadJsonButton from "./DownloadJsonButton";

interface ResultTableType {
  metricInformation: MetricType;
  results: EvaluationResultType;
}

function createData(
  result: string,
  value: string,
  value_type: 'json' | 'image' | 'text',
  evaluation: string | undefined,
  description: string
) {
  return { result, value, value_type, evaluation, description };
}


export default function ResultTable({metricInformation, results}: ResultTableType): ReactElement {
  const rows = [];
  const [naturalSize, setNaturalSize] = useState({ width: 0, height: 0 });
  const handleImageLoad = (event) => {
    const { naturalWidth, naturalHeight } = event.target;
    setNaturalSize({ width: naturalWidth, height: naturalHeight });
  };
  const renderedWidth = naturalSize.width > 300 ? 300 : naturalSize.width;
  const renderedHeight = Math.round(naturalSize.height / (naturalSize.width / renderedWidth));
  metricInformation.results.forEach((v, index) => {
    let evaluation = '';
    if (v.scores) {
      const floatValue = parseFloat(results.results[index]);
      for (const score of v.scores) {
        const range = score.range;
        if (floatValue < range[1] || range[1] == null) {
          evaluation = score.description;
          break;
        }
      }
    }
    rows.push(createData(v.name, results.results[index], v.type, evaluation, v.description));
  })

  return (
    <TableContainer component={Paper as ReactNode}>
      <Table aria-label="metric evaluation result table">
        <TableHead>
          <TableRow>
            <TableCell width="30%">Result</TableCell>
            <TableCell width="25%">Value</TableCell>
            <TableCell width="20%">Evaluation</TableCell>
            <TableCell width="25%">Description</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {rows && rows.map((row, index) => (
              <TableRow
                key={row.result + "_" + index}
              >
                <TableCell component="th" scope="row">
                  {row.result}
                </TableCell>
                {
                  row.value_type === 'image' &&
                    <TableCell>
                      <Grid container direction="column">
                        <Grid item>
                          <Link href={row.value} target="_blank">
                            <img
                              alt={`evaluation_result_${row.result}`}
                              onLoad={handleImageLoad}
                              src={row.value}
                              width={renderedWidth}
                              height={renderedHeight}
                            />
                          </Link>
                        </Grid>
                      </Grid>
                    </TableCell>
                }
                {
                  row.value_type === 'json' &&
                  <TableCell>
                    <DownloadJsonButton data={row.value} />
                  </TableCell>
                }
                {
                  row.value_type === 'text' &&
                  <TableCell>
                    {parseFloat(row.value).toFixed(2)}
                  </TableCell>
                }
                <TableCell>{row.evaluation}</TableCell>
                <TableCell>{row.description}</TableCell>
              </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
}