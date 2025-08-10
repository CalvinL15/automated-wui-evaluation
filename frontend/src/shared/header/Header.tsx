import React, {PropsWithChildren, ReactElement} from 'react';

import {
  HeaderAreaStyled,
  HeaderBoxStyled,
  HeaderContainerStyled,
  HeaderDescriptionStyled,
  HeaderStyled,
  HeaderTitleStyled
} from './Header.styled';

export interface HeaderAreaProps {
  alignContent?: 'start' | 'end';
  alignItems?: 'start' | 'center' | 'end';
  gap?: string;
}

export interface HeaderTitleProps {
  title: string;
}

export function HeaderTitle(props: PropsWithChildren<HeaderTitleProps>): ReactElement {
  const {title} = props;
  return <HeaderTitleStyled>{title}</HeaderTitleStyled>;
}

export function HeaderDescription(props: PropsWithChildren<{description: string | ReactElement}>): ReactElement {
  const {description} = props;
  return (
    <HeaderDescriptionStyled>
      {description}
    </HeaderDescriptionStyled>
  );
}

export function HeaderArea(props: PropsWithChildren<HeaderAreaProps>): ReactElement {
  const {alignContent, alignItems, gap, children} = props;
  return (
    <HeaderAreaStyled
      gap={gap}
      alignItems={alignItems}
      alignContent={alignContent}
    >
      {children}
    </HeaderAreaStyled>
  );
}

export function HeaderBox(props: PropsWithChildren<{gap: string}>): ReactElement {
  const {children, gap} = props;
  return (
    <HeaderBoxStyled gap={gap}>
      {children}
    </HeaderBoxStyled>
  );
}

export function HeaderContainer(props: PropsWithChildren<{alignItems?: 'start' | 'center' | 'end'}>): ReactElement {
  const {children, alignItems} = props;
  return (
    <HeaderContainerStyled alignItems={alignItems}>
      {children}
    </HeaderContainerStyled>
  );
}

export function Header(props: PropsWithChildren<unknown>): ReactElement {
  const {children} = props;
  return <HeaderStyled>{children}</HeaderStyled>;
}

Header.Container = HeaderContainer;
Header.Area = HeaderArea;
Header.Box = HeaderBox;
Header.Title = HeaderTitle;
Header.Description = HeaderDescription;

export default Header;
