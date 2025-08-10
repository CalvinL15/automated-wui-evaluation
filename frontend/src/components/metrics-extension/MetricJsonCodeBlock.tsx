import {Grid} from "@mui/material";
import React from "react";
import {a11yLight, CodeBlock} from "react-code-blocks";

export default function MetricJsonCodeBlock() {
  const code = `    {
      "m11": {
          "name": "Subband entropy",
          "description": "A measure of clutter based on measure of the efficiency with which the image can be encoded while maintaining perceptual image quality.",
          "accepted_input": [
            "url",
            "html",
            "png"
          ],
          "preprocessing": {
            "grayscale_conversion_required": false,
            "segmentation_required": false,
            "jpeg_conversion_required": false,
            "dom_analysis_required": false,
            "lab_conversion_required": true
          },
          "references": [
            {
              "title": "R. Rosenholtz, Y. Li, and L. Nakano (2007). Measuring Visual Clutter. Journal of Vision August 2007, vol. 7, 17, pp. 1-22.",
              "url": "https://doi.org/10.1167/7.2.17"
            },
            {
              "title": "A. Miniukovich and A. De Angeli (2015). Computation of Interface Aesthetics. CHI'15: Proceedings of the 33rd Annual ACM Conference on Human Factor in Computing Systems, pp. 1163-1172.",
              "url": "https://doi.org/10.1145/2702123.2702575"
            },
            {
              "title": "A. Oulasvirta, S. De Pascale, J. Koch, T. Langerak, J. Jokinen, K. Todi, M. Laine, M. Kristhombuge, Z. Yuxi, A. Miniukovich, G. Palmas, T. Weinkauf (2018).  Aalto Interface Metrics (AIM): A Service and Codebase for Computational GUI Evaluation. Adjunct Proceedings of the 31st Annual ACM Symposium on User Interface Software and Technology (UIST '18 Adjunct), pp. 16-19.",
              "url": "https://doi.org/10.1145/3266037.3266087"
            }
          ],
          "results": [
            {
              "name": "Subband entropy",
              "description": "A higher entropy value indicates increased visual clutter within the image. The interpretation of these values is taken from the scoring system used in AIM.",
              "type": "text",
              "scores": [
                {
                  "range": [
                    0,
                    2.7153
                  ],
                  "description": "good"
                },
                {
                  "range": [
                    2.7154,
                    3.4693
                  ],
                  "description": "normal"
                },
                {
                  "range": [
                    3.4694,
                    null
                  ],
                  "description": "bad"
                }
              ]
            }
          ]
        }
  }`
  return (
    <Grid marginTop='1rem' marginBottom='1rem' maxWidth={'1400px'} xs={12}>
      <CodeBlock
        text={code}
        language='json'
        showLineNumbers={false}
        theme={a11yLight}
        wraplines
      />
    </Grid>
  );
}