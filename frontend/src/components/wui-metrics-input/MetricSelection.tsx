import {ExpandMoreOutlined} from "@mui/icons-material";
import LinkIcon from '@mui/icons-material/Link';
import FolderZipIcon from '@mui/icons-material/FolderZip';
import HtmlIcon from '@mui/icons-material/Html';
import ImageIcon from '@mui/icons-material/Image';
import {
  Accordion,
  AccordionDetails,
  AccordionSummary,
  Autocomplete, Button,
  Divider,
  Grid,
  TextField,
  Typography
} from "@mui/material";
import React, {ReactElement, useContext, useEffect, useState} from "react";
import { useNavigate } from "react-router-dom";

import InputContext from "../../context/InputContext";
import RequestsContext from "../../context/RequestsContext";
import CustomTypography from "../../shared/typography/Typography";
import {EvaluationButtonWrap, MetricSelectionWrap} from "../../shared/wrappers/ElementWrap";
import { MetricType } from "../../types/MetricType";
import { FileInputRequestType,UrlInputRequestType } from "../../types/RequestType"

interface MetricSelectionType {
  metrics: MetricType[] | undefined;
}

export default function MetricSelection({metrics}: MetricSelectionType): ReactElement {
  const { urlInputs, fileInputs } = useContext(InputContext);
  const navigate = useNavigate();
  const { setUrlRequests, setFileRequests } = useContext(RequestsContext);
  const [isEvaluatingInputs, setIsEvaluatingInputs] = useState(false);
  const [globalAutocompleteValues, setGlobalAutocompleteValues] = useState([]);
  const [urlAutocompleteValues, setUrlAutocompleteValues] = useState(
    urlInputs.reduce((acc, input) => {
      acc[input] = [];
      return acc;
    }, {})
  );

  const [fileAutocompleteValues, setFileAutocompleteValues] = useState(
    fileInputs.reduce((acc, input) => {
      acc[input.filename] = [];
      return acc;
    }, {})
  );

  // State to control the disabled status of the button
  const [isButtonDisabled, setIsButtonDisabled] = useState(false);

  // Function to check if any key has an empty value in the autocomplete values
  const checkForEmptyValues = (autocompleteValues) => {
    return Object.values(autocompleteValues).some(arr => arr.length === 0);
  };

  useEffect(() => {
    // Determine if the button should be disabled
    const disableButton = checkForEmptyValues(urlAutocompleteValues) || checkForEmptyValues(fileAutocompleteValues);
    setIsButtonDisabled(disableButton);
  }, [urlAutocompleteValues, fileAutocompleteValues]);

  // Handlers for changing Autocomplete values

  const handleUrlAutocompleteChange = (index, newValue) => {
    const urlInput = urlInputs[index];
    setUrlAutocompleteValues(prevSelectedMetrics => ({
      ...prevSelectedMetrics,
      [urlInput]: newValue
    }));
  }

  const handleFileAutocompleteChange = (index, newValue) => {
    const fileInput = fileInputs[index].filename;
    setFileAutocompleteValues(prevSelectedMetrics => ({
      ...prevSelectedMetrics,
      [fileInput]: newValue
    }));
  }

  const metricsArray = Object.entries(metrics).map(([key, value]) => {
    return {
      label: value.name,
      value: key,
      acceptedInputs: value.accepted_input
    };
  });

  // not all metrics are available for PNG input format
  const metricsArrayPng = metricsArray.filter((metric) => metric.acceptedInputs.includes("png"));

  const handleGlobalAutocompleteChange = (newGlobalAutocompleteValues) => {
    const addedMetrics = newGlobalAutocompleteValues.filter(metric => !globalAutocompleteValues.includes(metric));
    const removedMetrics = globalAutocompleteValues.filter(metric => !newGlobalAutocompleteValues.includes(metric));

    // Add newly added metrics to all specific autocompletes
    if (addedMetrics.length > 0) {
      const updatedUrlAutocompleteValues = { ...urlAutocompleteValues };
      for (const urlInput in updatedUrlAutocompleteValues) {
        const isMetricAdded = updatedUrlAutocompleteValues[urlInput].some(metric => {
          return addedMetrics.some(addedMetric => addedMetric.value === metric.value);
        });
        if (!isMetricAdded) {
          updatedUrlAutocompleteValues[urlInput] = [...updatedUrlAutocompleteValues[urlInput], ...addedMetrics];
        }
      }
      setUrlAutocompleteValues(updatedUrlAutocompleteValues);

      const updatedFileAutocompleteValues = { ...fileAutocompleteValues };
      for (const fileInput in updatedFileAutocompleteValues) {
        const isMetricAdded = updatedFileAutocompleteValues[fileInput].some(metric => {
          return addedMetrics.some(addedMetric => addedMetric.value === metric.value);
        });

        const isMetricComputable = (fileInput.includes("png") &&
          !(addedMetrics[0].acceptedInputs.includes("png"))) ?
          false : true;

        if (!isMetricAdded && isMetricComputable) {
          updatedFileAutocompleteValues[fileInput] = [...updatedFileAutocompleteValues[fileInput], ...addedMetrics];
        }
      }
      setFileAutocompleteValues(updatedFileAutocompleteValues);
    }

    // Remove deselected metrics from all specific autocompletes
    if (removedMetrics.length > 0) {
      const updatedUrlAutocompleteValues = { ...urlAutocompleteValues };
      for (const urlInput in updatedUrlAutocompleteValues) {
        updatedUrlAutocompleteValues[urlInput] = updatedUrlAutocompleteValues[urlInput].filter(metric => !removedMetrics.includes(metric));
      }
      setUrlAutocompleteValues(updatedUrlAutocompleteValues);

      const updatedFileAutocompleteValues = { ...fileAutocompleteValues };
      for (const fileInput in updatedFileAutocompleteValues) {
        updatedFileAutocompleteValues[fileInput] = updatedFileAutocompleteValues[fileInput].filter(metric => !removedMetrics.includes(metric));
      }
      setFileAutocompleteValues(updatedFileAutocompleteValues);
    }

    setGlobalAutocompleteValues(newGlobalAutocompleteValues);
  }

  const handleButtonClick = async () => {
    setIsEvaluatingInputs(true);
    const urlInputRequests: UrlInputRequestType[] = []
    const fileInputRequests: FileInputRequestType[] = []

    // prepare inputs
    Object.keys(urlAutocompleteValues).forEach(key => {
      const data = urlAutocompleteValues[key];
      const urlInputRequest: UrlInputRequestType = {
        url: key,
        metrics: data.map(obj => obj.value)
      }
      urlInputRequests.push(urlInputRequest);
    });

    Object.keys(fileAutocompleteValues).forEach(key => {
      const data = fileAutocompleteValues[key];
      const fileData: File = fileInputs.find(f => key === f.filename).file as File;

      const fileInputRequest: FileInputRequestType = {
        file: fileData,
        metrics: data.map(obj => obj.value)
      }
      fileInputRequests.push(fileInputRequest);
    });

    setFileRequests(fileInputRequests)
    setUrlRequests(urlInputRequests);
    navigate("/result");
  }

  return (
    <MetricSelectionWrap>
      <Grid  container direction='column' spacing={2}>
        <Grid item xs={12}>
          <CustomTypography>
            For each input, at minimum 1 metric must be selected!
          </CustomTypography>
        </Grid>
        <Divider />
        {
          urlInputs.length + fileInputs.length > 1 &&
          <Grid item xs={12}>
            <Typography sx={{ fontWeight: 600, mt: '0.5rem', mb: '1rem' }} variant="subtitle1" color="textPrimary" gutterBottom>
              Select Global Metrics (applies to all inputs unless overridden by individual input settings)
            </Typography>
            <Typography variant={'body2'} sx={{mb: '1rem' }}>
              Note: Selecting a metric here will apply it to all inputs with compatible format type.
              You can also customize metrics for each input individually, which will override these global selections.
            </Typography>
            <Autocomplete
              multiple
              renderInput={
                (params) => <TextField {...params} label="Select metrics!" />
              }
              onChange={(_, newValue) => {
                handleGlobalAutocompleteChange(newValue)
              }}
              isOptionEqualToValue={(option, value) => option.value === value.value}
              options={metricsArray}
              getOptionLabel={(option) => option.label}
              size='small'
            />
            <Divider />
          </Grid>
        }
        <Grid item xs={12}>
          <Typography sx={{ fontWeight: 600, marginTop: '1rem', marginBottom: '0.5rem' }} variant="subtitle1" color="textPrimary" gutterBottom>Input(s)</Typography>
          {
            urlInputs.map((url, index) => (
              <Accordion key={`${index}__${url}`} defaultExpanded>
                <AccordionSummary
                  expandIcon={<ExpandMoreOutlined />}
                  aria-controls={`${index}__${url}__content`}
                >
                  <Grid container spacing={2}>
                    <Grid item>
                      <LinkIcon />
                    </Grid>
                    <Grid item>
                      <Typography color="textSecondary">{url}</Typography>
                    </Grid>
                  </Grid>
                </AccordionSummary>
                <AccordionDetails>
                  <Autocomplete
                    key={index}
                    value={urlAutocompleteValues[url]}
                    multiple
                    renderInput={
                      (params) => <TextField {...params} label="Select metrics!" />
                    }
                    onChange={(_, newValue) => {
                      handleUrlAutocompleteChange(index, newValue);
                    }}
                    isOptionEqualToValue={(option, value) => option.value === value.value}
                    options={metricsArray}
                    getOptionLabel={(option) => option.label}
                    size='small'
                  />
                </AccordionDetails>
              </Accordion>
            ))
          }
          {
            fileInputs.map((file, index) => (
              <Accordion key={`${index}__${file.filename}`} defaultExpanded>
                <AccordionSummary
                  expandIcon={<ExpandMoreOutlined />}
                  aria-controls={`${index}__${file.filename}__content`}
                >
                  <Grid container spacing={2}>
                    <Grid item>
                      {
                        file.fileType === 'application/zip' && <FolderZipIcon />
                      }
                      {
                        file.fileType === 'text/html' && <HtmlIcon />
                      }
                      {
                        file.fileType === 'image/png' && <ImageIcon />
                      }
                    </Grid>
                    <Grid item>
                      <Typography color="textSecondary">{file.filename}</Typography>
                    </Grid>
                  </Grid>
                </AccordionSummary>
                <AccordionDetails>
                  <Autocomplete
                    key={index}
                    value={fileAutocompleteValues[file.filename]}
                    multiple
                    renderInput={
                      (params) => <TextField {...params} label="Select metrics!" />
                    }
                    onChange={(_, newValue) => {
                      handleFileAutocompleteChange(index, newValue);
                    }}
                    isOptionEqualToValue={(option, value) => option.value === value.value}
                    options={file.filename.includes("png") ? metricsArrayPng : metricsArray}
                    getOptionLabel={(option) => option.label}
                    size='small'
                  />
                </AccordionDetails>
              </Accordion>
            ))
          }
        </Grid>
        <Grid item xs={12} alignSelf="self-end">
          <EvaluationButtonWrap>
              <Button
                color='primary'
                variant="contained"
                disabled={isButtonDisabled || isEvaluatingInputs}
                onClick={handleButtonClick}
              >
                Evaluate WUI input(s)!
              </Button>
          </EvaluationButtonWrap>
        </Grid>
        <Divider />
        <Grid></Grid>
      </Grid>
    </MetricSelectionWrap>
  )
}