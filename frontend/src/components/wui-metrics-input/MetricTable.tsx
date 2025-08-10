import {Link, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Tooltip} from "@mui/material";
import React, {ReactElement, ReactNode} from 'react';

import {AcceptedInputType, MetricType, ReferenceType} from "@/types/MetricType";

function createData(
  id: string,
  name: string,
  description: string,
  acceptedInput: AcceptedInputType[],
  references: ReferenceType[]
) {
  return { id, name, description, acceptedInput, references };
}

interface MetricTableType {
  metrics: Record<string, MetricType> | undefined
}

export default function MetricTable({metrics}: MetricTableType): ReactElement {
  const rows = [];
  if (!metrics) return;

  Object.keys(metrics).forEach(metricKey => {
    const metric = metrics[metricKey];
    rows.push(createData(metricKey, metric.name, metric.description, metric.accepted_input, metric.references));
  });

  return (
    <TableContainer component={Paper as ReactNode}>
      <Table aria-label="metric table">
        <TableHead>
          <TableRow>
            <TableCell width="30%">Name</TableCell>
            <TableCell width="30%">Description</TableCell>
            <TableCell width="25%">Accepted Formats</TableCell>
            <TableCell width="15%">References</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {rows && rows.map((row) => (
            <TableRow
              key={row.id}
            >
              <TableCell component="th" scope="row">
                {row.name}
              </TableCell>
              <TableCell>{row.description}</TableCell>
              <TableCell>{row.acceptedInput.join(', ')}</TableCell>
              <TableCell>
                {row.references.reduce((acc: ReactElement, value: ReferenceType, index: number) => {
                  const isLast = index === row.references.length - 1;
                  const link =
                    <Tooltip key={`${row.id}_${value.title}`} describeChild title={value.title}>
                      <Link href={value.url} rel="noreferrer" target="_blank">
                        {`[${index + 1}]`}
                      </Link>
                    </Tooltip>
                  if (isLast) {
                    return [...acc, link];
                  } else {
                    return [...acc, link, ', '];
                  }
                }, [])}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
}