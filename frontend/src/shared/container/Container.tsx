import styled from "@emotion/styled";
import React, { ReactElement, ReactNode } from "react";

interface ContainerPropsType {
  children: ReactNode | ReactNode[];
}

const StyledContainer = styled.div`
  background-color: #fff;
  border-radius: 6px;
  border: 1px solid rgb(226, 226, 228);
  align-self: flex-start;
  width: 100%;
  margin-bottom: 1rem;
`;

export default function Container({children}: ContainerPropsType): ReactElement {
  return <StyledContainer>{children}</StyledContainer>;
}