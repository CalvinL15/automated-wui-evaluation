import {Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow} from "@mui/material";
import React, {ReactElement, ReactNode} from 'react';

export default function MetricTable(): ReactElement {
  const rows = [
    {
      key: "name",
      description: <>The name of the metric</>
    },
    {
      key: "accepted_input",
      description: <>An array listing the types of inputs the metric accepts, which include the formats: <code>{'"url"'}</code>, <code>{'"png"'}</code>, and <code>{'"html"'}</code>.</>
    },
    {
      key: "description",
      description: <>The description of the metric</>
    },
    {
      key: "preprocessing",
      description: <>An object specifying any preprocessing steps required by the metric. Please refer to the table describing <code>preprocessing</code> object below.</>
    },
    {
      key: "references",
      description: <>An array of objects, each containing a <code>{'"title"'}</code> and <code>{'"url"'}</code> field, providing citations or relevant literature that supports the metric.</>
    },
    {
      key: "results",
      description: <>An array of <code>result</code> entries describing the expected results. Please refer to the table
        describing <code>result</code> below.</>
    }
  ];


  return (
    <TableContainer component={Paper as ReactNode}>
      <Table aria-label="metric table">
        <TableHead>
          <TableRow>
            <TableCell width="30%">Key</TableCell>
            <TableCell width="70%">Description</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {rows && rows.map((row) => (
            <TableRow
              key={row.key + "_" + row.description}
            >
              <TableCell component="th" scope="row">
                <b>{row.key}</b>
              </TableCell>
              <TableCell>{row.description}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
}