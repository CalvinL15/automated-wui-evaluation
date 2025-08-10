import 'filepond/dist/filepond.min.css';
import 'filepond-plugin-image-preview/dist/filepond-plugin-image-preview.css';

import {Box, Button, Divider, Grid} from '@mui/material';
import { TextField, Typography } from "@mui/material";
import {FilePondFile, FilePondInitialFile} from "filepond";
import FilePondPluginFileValidateType from 'filepond-plugin-file-validate-type';
import FilePondPluginImageExifOrientation from 'filepond-plugin-image-exif-orientation';
import FilePondPluginImagePreview from 'filepond-plugin-image-preview';
import {HTTPError} from 'ky';
import {useSnackbar} from "notistack";
import React, {ReactElement, useState} from 'react';
import { FilePond, registerPlugin } from 'react-filepond';
import * as Yup from 'yup';

import {useProcessMetricExtensionRequest} from "../../client/mutations";
import {ButtonWrap} from "../../shared/wrappers/ElementWrap";
import {MetricExtensionRequestMetadataType} from "../../types/MetricExtensionRequestMetadataType";
import {emailValidationSchema, urlValidationSchema} from "../../validationSchema/validationSchema";

// Register the plugins
registerPlugin(FilePondPluginImageExifOrientation, FilePondPluginFileValidateType, FilePondPluginImagePreview);

const acceptedFileTypes = [
  'application/json',
  'text/x-python',
  'text/x-python-script',
  'text/plain'
];

export default function MetricExtensionInputReceiver(): ReactElement {
  const {enqueueSnackbar} = useSnackbar();
  const {mutateAsync: ProcessMetricExtensionRequest} = useProcessMetricExtensionRequest();
  const [fileInputs, setFileInputs] = useState<FilePondFile[]>([]);
  const [downloadLinksString, setDownloadLinksString] = useState('');
  const [emailAddress, setEmailAddress] = useState('');
  const [errorEmailAddress, setErrorEmailAddress] = useState('');
  const [errorUrl, setErrorUrl] = useState('');
  const [isConfirming, setIsConfirming] = useState(false);

  const validateEmailAddress = async () => {
    try {
      await emailValidationSchema.validate(emailAddress);
      setErrorEmailAddress('');
    } catch (err) {
      if (err instanceof Yup.ValidationError) {
        setErrorEmailAddress(err.message);
      }
    }
  };

  const validateUrls = async () => {
    const downloadLinks = downloadLinksString.split(",");
    try {
      const tempDownloadLinks = await Promise.all(
        downloadLinks.map(async (url) => {
          const trimmedUrl = url.trim();
          const transformedUrl = await urlValidationSchema.validate(trimmedUrl);
          return transformedUrl;
        })
      );
      setErrorUrl('');
      setDownloadLinksString(tempDownloadLinks.join(", "));
    } catch (err) {
      if (err instanceof Yup.ValidationError) {
        setErrorUrl(err.message);
      }
    }
  }

  const areRequiredFilesUploaded = () => {
    let isMetricImplementationUploaded = false;
    let isMetricConfigJsonUploaded = false;
    let isMetricRequirementsUploaded = false;
    fileInputs.forEach((fileInput) => {
      if (fileInput.filename === "requirements.txt") {
        isMetricRequirementsUploaded = true;
      } else if (fileInput.filename === "metric.json") {
        isMetricConfigJsonUploaded = true;
      } else if (fileInput.filename.includes(".py") && /^[^_]+_.*\.py$/.test(fileInput.filename)) {
        isMetricImplementationUploaded = true;
      }
    });
    return isMetricImplementationUploaded && isMetricConfigJsonUploaded && isMetricRequirementsUploaded;
  }

  // trigger API call after confirm button is clicked
  const handleButtonClick = async () => {
    setIsConfirming(true);
    const downloadLinks: string[] = downloadLinksString.split(",").map(link => {
      return link.trim();
    });

    const files: File[] = fileInputs.map(file => {
      return file as File;
    });

    const metricExtensionRequestMetadata: MetricExtensionRequestMetadataType = {
      download_links: downloadLinks,
      email_address: emailAddress
    }

    await ProcessMetricExtensionRequest({files, metricExtensionRequestMetadata}, {
      onSuccess: () => {
        // clear value
        setFileInputs([]);
        setEmailAddress('');
        setDownloadLinksString('');
        setIsConfirming(false);
        enqueueSnackbar('Metric extension request submitted successfully! Your request will be reviewed manually, as soon as possible!', {variant: 'success'});
      },
      onError: async (err) => {
        const errorMessage = err instanceof HTTPError ? await err.response.text() : 'An unknown error occurred';
        enqueueSnackbar(`Failed to submit metric extension request: ${errorMessage}`, { variant: 'error' });
        setIsConfirming(false);
      }
    });
  }

  return (
    <Grid item alignSelf='center' justifyContent='center' width='100%'>
      <Box sx={{mb: '1.5rem'}}>
        <Typography>
          Please read the <a href='#metric_extension_guide'>Metric Extension Guide section</a> thoroughly for detailed instructions on preparing the required files for a successful metric extension request!
        </Typography>
      </Box>
      <Divider />
      <Box sx={{mt: '1rem'}}>
        <Grid container direction='column' spacing={2}>
          <Grid item xs={12}>
            <Typography variant="body2" gutterBottom>
              Required files: metric implementation class in Python (naming format: <code>*_*.py</code>), metric.json, and requirements.txt.
            </Typography>
            <FilePond
              files={fileInputs as FilePondInitialFile[]}
              onupdatefiles={setFileInputs}
              allowMultiple={true}
              maxFiles={3}
              dropValidation={true}
              name='files'
              labelIdle={`Drag & Drop files or click the dropzone area to <span class="filepond--label-action">Browse</span>!`}
              allowFileTypeValidation
              acceptedFileTypes={acceptedFileTypes}
              credits={false}
            />
          </Grid>
          <Grid item xs={12}>
            <Typography variant="body1" fontWeight={600} gutterBottom>Download link(s) for required computational model(s)</Typography>
            <Typography variant="body2" gutterBottom>
              Separate each download link (URL) with a comma. Leave empty if not needed.
            </Typography>
            <TextField
              value={downloadLinksString}
              fullWidth
              onChange={(e) => setDownloadLinksString(e.target.value)}
              onBlur={validateUrls}
              error={Boolean(errorUrl)}
              helperText={errorUrl ? errorUrl + " Ensure that URLs are separated correctly!" : ""}
              sx={{mb: '1rem'}}
              label='Download link(s)'
            />
          </Grid>
          <Grid item xs={6}>
            <Typography variant="body1" fontWeight={600} gutterBottom>Email address</Typography>
            <Typography variant="body2" gutterBottom>
              Optional. If you choose to provide one, it will be used solely for correspondence related to your metric extension request.
            </Typography>
            <TextField
              fullWidth
              size={'small'}
              value={emailAddress}
              onChange={(e) => setEmailAddress(e.target.value)}
              onBlur={validateEmailAddress}
              error={Boolean(errorEmailAddress)}
              helperText={errorEmailAddress}
              label='Email address'
            />
          </Grid>
          <Grid item xs={12} alignSelf='self-end'>
            <ButtonWrap>
              <Button
                color='primary'
                variant="contained"
                disabled={!!errorUrl || !!errorEmailAddress || !areRequiredFilesUploaded() || isConfirming}
                onClick={handleButtonClick}
              >
                { isConfirming ? 'Processing request...' : 'Confirm' }
              </Button>
            </ButtonWrap>
          </Grid>
        </Grid>
      </Box>
    </Grid>
  )
}
