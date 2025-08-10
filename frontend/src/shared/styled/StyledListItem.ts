import styled from "@emotion/styled";
import {ListItem} from "@mui/material";

const StyledListItem = styled(ListItem)`
  background-color: #f0f0f0;
  margin-bottom: 8px;
  border-radius: 4px;
  &:hover {
    background-color: #e0e0e0;
  }
`;

export default StyledListItem;