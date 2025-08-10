import {Button, Divider, Grid, Link, Typography} from "@mui/material";
import React, { ReactElement, useState } from "react";

import Header from "../../shared/header/Header";
import {MetricsInformationContentWrap} from "../../shared/wrappers/ElementWrap";
import MetricInterfaceCodeBlock from "./MetricInterfaceCodeBlock";
import MetricJsonCodeBlock from "./MetricJsonCodeBlock";
import MetricJsonDefinitionTable from "./MetricJsonDefinitionTable";
import PreprocessingDefinitionTable from "./PreprocessingDefinitionTable";
import ResultDefinitionTable from "./ResultDefinitionTable";
import ImportMetricInterfaceCodeBlock from "./ImportMetricInterfaceCodeBlock";

export default function MetricExtensionGuide(): ReactElement {
  const [displayMetricJsonExample, setDisplayMetricJsonExample] = useState(false);
  const scrollToTop = () => {
    window.scrollTo({
      top: 0,
      behavior: 'smooth'
    });
  };
  return (
    <Grid id='metric_extension_guide'>
      <Header>
        <Header.Container>
          <Header.Box gap='2px'>
            <Header.Title title={'Metrics Extension Guide'} />
          </Header.Box>
        </Header.Container>
      </Header>
      <MetricsInformationContentWrap>
        <Typography sx={{mb: '1rem'}}>
          This platform is designed to be highly extensible. You can propose a new metric by following the guidelines described below.
        </Typography>
        <Typography sx={{mb: '1rem'}}>
          You need to upload these following files:
        </Typography>
        <ul>
          <li>
            The metric implementation file, implemented as a Python class. It <b>must</b> implement the <code>MetricInterface</code> class shown below.
            <MetricInterfaceCodeBlock />

            <Typography variant="body1" gutterBottom  sx={{mb: '1rem'}}>
              To import the <code>MetricInterface</code> definition, you <b>must</b> add the following in the top of your metric implementation file:
            </Typography>
            <ImportMetricInterfaceCodeBlock />

            <Typography variant="body1" gutterBottom sx={{mb: '1rem'}}>
              You can find example of segments output <Link href={'/image_segmentation_output.json'} target="_blank">here</Link> and DOM analysis output <Link href={'/dom_analyzer_output.json'} target="_blank">here</Link>.
            </Typography>

            <Typography variant="body1" gutterBottom>
              In addition, the python file <b>must</b> adhere to a specific naming convention: <code>
              {`{metric_id}_{metric_description}.py`}
              </code>. For instance, <code>m1_x.py</code> is a valid filename, while <code>m1-x.py</code> is not.
            </Typography>
          </li>
          <br />
          <li>
            <Typography variant="body1" gutterBottom>
              A <b>metric.json</b> file specifying the details of the metric you are proposing. The JSON <b>must</b> follow this structure:
            </Typography>
            <ul>
              <li>
                <Typography variant="body1" gutterBottom>
                  A metric id as the key, corresponding to the <code>{'{metric_id}'}</code> in the metric implementation filename.
                </Typography>
              </li>
              <li>
                <Typography variant="body1" gutterBottom sx={{mb: '2rem'}}>
                  Within this key, provide the following fields:
                </Typography>
                <MetricJsonDefinitionTable />
                <Typography variant="body2" sx={{mt: '2rem'}}>
                  Table describing the <code>preprocessing</code> object
                </Typography>
                <PreprocessingDefinitionTable />
                <Typography variant="body2" sx={{mt: '2rem'}}>
                  Table describing the <code>result</code> entry
                </Typography>
                <ResultDefinitionTable />
                <Button
                  variant="contained"
                  sx={{textTransform: 'initial', mt: '2rem'}}
                  onClick={() => setDisplayMetricJsonExample(!displayMetricJsonExample)}
                >
                  {
                    !displayMetricJsonExample ? 'Click here to display an example of valid metric.json' : 'Click here to hide the example'
                  }
                </Button>
                {
                  displayMetricJsonExample && <MetricJsonCodeBlock />
                }
              </li>
            </ul>
          </li>
          <br />
          <li>
            <Typography variant="body1" gutterBottom sx={{mb: '1rem'}}>
              A <b>requirements.txt</b> file listing the modules and packages needed for the metric implementation to run correctly. It can be generated with the pip command <code>{'`pip freeze > requirements.txt`'}</code>.
            </Typography>
            <Typography variant="body1">
              Alternatively, for Conda environments, the equivalent file can be created with <code>{'`conda list -e > requirements.txt`'}</code>. Both formats are accepted, but only one is needed.
            </Typography>
          </li>
        </ul>
        <br />
        <Divider sx={{mb: '2rem'}}/>
        <Typography variant="body1" sx={{mb: '2rem'}}>
          <b>Important</b>: For metrics requiring computational models (e.g., Keras .h5 files), please supply the download links for these models using the provided interface.
          Do not attempt to upload model files directly through the file uploader! Additionally, you may optionally provide an email address via the interface for correspondence regarding your metric submission.
        </Typography>
        <Button onClick={scrollToTop}>
          Scroll to top of the page
        </Button>
      </MetricsInformationContentWrap>
    </Grid>
  )
}