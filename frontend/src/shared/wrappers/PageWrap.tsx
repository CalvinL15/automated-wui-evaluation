import styled from "@emotion/styled";
import React, { ReactElement, ReactNode } from "react";
interface PageWrapPropsType {
  children: ReactNode | ReactNode[];
}

const StyledPageWrap = styled.div`
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  min-width: 100vw;
  background-color: #F1F1F1;
`;

export default function PageWrap({children}: PageWrapPropsType): ReactElement {
  return <StyledPageWrap>{children}</StyledPageWrap>;
}