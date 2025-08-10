import styled from '@emotion/styled';

export const HeaderStyled = styled.header`
  position: sticky;
  top: 0;
  background-color: #FFFFFF;
  width: 100%;
`;

export const HeaderAreaStyled = styled.div`
  height: 100%;
  flex-shrink: 0;
  display: flex;
  gap: ${({ gap }) => gap ?? '8px'};
  align-items: ${({ alignItems }) => alignItems};
  align-content: ${({ alignContent }) => alignContent};
`;

export const HeaderBoxStyled = styled.div`
  display: flex;
  justify-content: flex-start;
  align-items: flex-start;
  flex-direction: column;
  gap: ${({gap}) => gap};
`

export const HeaderTitleStyled = styled.h3`
  font-weight: bold;
  font-size: 24px;
  flex-shrink: 0;
  line-height: 32px;
  margin: 0;
  margin-inline-end: 8px;
`

export const HeaderDescriptionStyled = styled.p`
  font-size: 12px;
  line-height: 16px;
  color: rgb(84, 84, 89);
  margin: 0;
  max-width: 600px;
`

export const HeaderContainerStyled = styled.section`
  height: 100%;
  display: flex;
  padding: 24px 40px;
  border-bottom: 1px solid rgb(226, 226, 228);
  justify-content: space-between;
  align-items: ${({ alignItems }) => alignItems ?? 'center'};
`
