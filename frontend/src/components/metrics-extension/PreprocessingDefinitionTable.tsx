import {Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow} from "@mui/material";
import React, {ReactElement, ReactNode} from 'react';

export default function PreprocessingDefinitionTable(): ReactElement {
  const rows = [
    {
      key: "grayscale_conversion_required",
      description: "A boolean value specifying whether grayscale conversion is required by the metric."
    },
    {
      key: "jpeg_conversion_required",
      description: "A boolean value specifying whether jpeg conversion is required by the metric."
    },
    {
      key: "segmentation_required",
      description: "A boolean value specifying whether image segmentation is required by the metric."
    },
    {
      key: "dom_analysis_required",
      description: "A boolean value specifying whether DOM analysis is required by the metric."
    },
    {
      key: "lab_conversion_required",
      description: " A boolean value specifying whether image conversion to CIELab color space is required by the metric."
    },
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