import styled from "@emotion/styled";
import Typography from '@mui/material/Typography';
import React, { ReactElement, ReactNode } from 'react';

interface TypographyPropsType {
  children: ReactNode | ReactNode[];
}

const StyledTypography = styled(Typography)`
  color: rgb(84, 84, 89);
  margin: 0 0 1rem;
  text-justify: inter-word;
`;

export default function CustomTypography({children}: TypographyPropsType): ReactElement {
  return <StyledTypography>{children}</StyledTypography>;
}
