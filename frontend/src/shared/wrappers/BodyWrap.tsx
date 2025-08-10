import styled from "@emotion/styled";
import React, { ReactElement, ReactNode } from "react";

interface BodyWrapPropsType {
  children: ReactNode | ReactNode[];
}

const StyledBodyWrap = styled.main`
  flex: 1 1 auto;
  display: flex;
  overflow-y: auto;
  padding: 1rem;
  @media (min-width: 800px) {
    padding: 2rem;
  }
`;
export default function BodyWrap({children}: BodyWrapPropsType): ReactElement {
  return <StyledBodyWrap>{children}</StyledBodyWrap>;
}
