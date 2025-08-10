import DeleteIcon from '@mui/icons-material/Delete';
import {Button, Grid, IconButton, List, ListItemText, TextField, Typography} from "@mui/material";
import React, {ReactElement, useContext, useState} from "react";
import * as Yup from 'yup';

import InputContext from "../../context/InputContext";
import StyledListItem from '../../shared/styled/StyledListItem';
import {urlValidationSchema} from "../../validationSchema/validationSchema";

export default function URLInput(): ReactElement {
  const { urlInputs, fileInputs, setUrlInputs } = useContext(InputContext);
  const [currentUrl, setCurrentUrl] = useState('');
  const [error, setError] = useState('');

  const validateCurrentUrl = async () => {
    try {
      const transformedUrl = await urlValidationSchema.validate(currentUrl);
      setError('');
      if (typeof transformedUrl == 'string') {
        setCurrentUrl(transformedUrl);
      }
    } catch (err) {
      if (err instanceof Yup.ValidationError) {
        setError(err.message);
      }
    }
  }

  const handleAddUrl = async () => {
    try {
      const transformedUrl = await urlValidationSchema.validate(currentUrl);
      setError('');
      if (typeof transformedUrl == 'string') {
        setUrlInputs((prevUrls) => [...prevUrls, transformedUrl]);
      }
      setCurrentUrl('');
    } catch (err) {
      if (err instanceof Yup.ValidationError) {
        setError(err.message);
      }
    }
  };

  const handleRemoveUrl = (index: number) => {
    const newUrls = urlInputs.filter((_, i) => i !== index);
    setUrlInputs(newUrls); // Assuming you want to decrement the count in your context
  };

  return (
    <>
      <Grid spacing={4} container item>
        <Grid item xs={9}>
          <TextField
            label='Input the URL of your WUI here!'
            disabled={urlInputs.length + fileInputs.length >= 5}
            size='small'
            variant='outlined'
            value={currentUrl}
            onChange={(e) => setCurrentUrl(e.target.value)}
            onBlur={validateCurrentUrl}
            fullWidth
            error={Boolean(error)}
            helperText={error}
          />
        </Grid>
        <Grid item xs={3}>
          <Button disabled={urlInputs.length + fileInputs.length >= 5 || !currentUrl} onClick={handleAddUrl}>
            Add URL
          </Button>
        </Grid>
        <Grid item xs={12}>
          <Typography component="h4" color="textPrimary">
            Current URL inputs
          </Typography>
          <List>
            {urlInputs.length > 0 ?
              urlInputs.map((url, index) => (
                <StyledListItem
                  key={index}
                  secondaryAction={
                    <IconButton edge="end" aria-label="delete" onClick={() => handleRemoveUrl(index)}>
                      <DeleteIcon />
                    </IconButton>
                  }
                >
                  <ListItemText primary={url} />
                </StyledListItem>
              )) :
              <Typography variant="body2" color="textSecondary">
                No URLs added yet.
              </Typography>
            }
          </List>
        </Grid>
      </Grid>
    </>
  )
}