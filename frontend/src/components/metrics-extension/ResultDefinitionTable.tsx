import {Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow} from "@mui/material";
import React, {ReactElement, ReactNode} from 'react';

export default function PreprocessingDefinitionTable(): ReactElement {
  const rows = [
    {
      key: "name",
      description: <>Name of the result</>
    },
    {
      key: "description",
      description: <>Optional description for the result. Leave it empty if there is no description</>
    },
    {
      key: "type",
      description: <>The result type (three values are possible: <code>{'"text"'}</code>, <code>{'"json"'}</code>, <code>{'"image"'}</code>).</>
    },
    {
      key: "scores",
      description: <>An array of objects, each containing a <code>&quot;range&quot;</code> and <code>&quot;description&quot;</code> field,
        which describe the meaning of the results within those intervals. This field is optional and can be omitted if such interpretations are not necessary.</>
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