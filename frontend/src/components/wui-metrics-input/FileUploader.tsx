import 'filepond/dist/filepond.min.css';
import 'filepond-plugin-image-preview/dist/filepond-plugin-image-preview.css';

import { Grid } from '@mui/material';
import {FilePondInitialFile} from "filepond";
import FilePondPluginFileValidateType from 'filepond-plugin-file-validate-type';
import FilePondPluginImageExifOrientation from 'filepond-plugin-image-exif-orientation';
import FilePondPluginImagePreview from 'filepond-plugin-image-preview';
import React, {ReactElement, useContext} from 'react';
import { FilePond, registerPlugin } from 'react-filepond';

import InputContext from "../../context/InputContext";

// Register the plugins
registerPlugin(FilePondPluginImageExifOrientation, FilePondPluginFileValidateType, FilePondPluginImagePreview);

const acceptedFileTypes = ['image/png', 'text/html', 'application/zip'];

export default function FileUploader(): ReactElement {
  const {fileInputs, setFileInputs} = useContext(InputContext);
  return (
    <Grid item alignSelf='center' justifyContent='center' width='100%'>
      <FilePond
        files={fileInputs as FilePondInitialFile[]}
        onupdatefiles={setFileInputs}
        allowMultiple={true}
        dropValidation={true}
        name='files'
        labelIdle={`Drag & Drop files or click the dropzone area to <span class="filepond--label-action">Browse</span>!`}
        allowFileTypeValidation
        acceptedFileTypes={acceptedFileTypes}
        credits={false}
      />
    </Grid>
  )
}
