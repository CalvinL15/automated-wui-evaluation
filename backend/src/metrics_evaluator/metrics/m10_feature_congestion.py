#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Metric: Feature congestion

Description: A measure of display cluster based upon extensive modeling of the saliency of elements of the input.

References:
    [1] R. Rosenholtz, Y. Li, J. Mansfield, and Z. Jin (2005). Feature Congestion: A Measure of Visual Clutter.
    CHI'05: Proceedings of the SIGCHI Conference on Human Factors in Computing Systems, pp. 761-770.
    DOI: https://doi.org/10.1167/6.6.827

    [2] R. Rosenholtz, Y. Li, and L. Nakano (2007). Measuring Visual Clutter.
    Journal of Vision August 2007, vol. 7, 17, pp. 1-22.",
    DOI: "https://doi.org/10.1167/7.2.17"

    [3] A. Miniukovich and A. De Angeli (2015). Computation of Interface Aesthetics.
    CHI'15: Proceedings of the 33rd Annual ACM Conference on Human Factor in Computing Systems, pp. 1163-1172.
    DOI: https://doi.org/10.1145/2702123.2702575

    [4] A. Oulasvirta, S. De Pascale, J. Koch, T. Langerak, J. Jokinen, K. Todi, M. Laine,
    M. Kristhombuge, Z. Yuxi, A. Miniukovich, G. Palmas, T. Weinkauf (2018).
    Aalto Interface Metrics (AIM): A Service and Codebase for Computational GUI Evaluation.
    Adjunct Proceedings of the 31st Annual ACM Symposium on User Interface Software and Technology, pp. 16-19.
    DOI: https://doi.org/10.1145/3266037.3266087
"""

from io import BytesIO
from typing import Optional, Dict, Any, Union, List

import numpy as np
from PIL import Image

from metrics_evaluator.metrics.metric_interface import MetricInterface
from commons.visual_clutter_utils import (
    conv2,
    RRoverlapconv,
    RRgaussfilter1D,
    RRcontrast1channel,
    orient_filtnew,
    poolnew,
    sumorients,
    HV,
    DD,
    normalize
)
from pydantic import HttpUrl
from pyrtools import pyramids, upConv


class Metric(MetricInterface):
    """
        Mostly based on the AIM's python implementation on the metric (available at: https://github.com/aalto-ui/aim),
        which is based on the MATLAB implementation by Rosenholtz et al, available at: http://hdl.handle.net/1721.1/37593
    """

    # private constants
    _LEVELS: int = 3  # number of levels (scales)
    _COLOR_POOL_SIGMA: float = 3  # std dev. of the Gaussian window for color clutter
    _CONTRAST_FILT_SIGMA: float = 1  # std dev. of the center-surround DoG1 filter used for computing the contrast
    _CONTRAST_POOL_SIGMA: float = 3 * _CONTRAST_FILT_SIGMA  # std dev. of the Gaussian window for contrast clutter
    _ORIENTATION_POOL_SIGMA: float = (7 / 2)  # std dev. of the Gaussian window for orientation clutter
    _ORIENTATION_NOISE: float = 0.001  # orientation noise in the saliency maps, value introduced by AIM (was epsilon
    # in the original implementation).

    # OPP_ENERGY constants (opponent energy)
    # As noted by Rosenholtz et al., These probably seem like arbitrary numbers,
    # but it's just trying to get three very different feature extraction methods to operate at basically the same
    # scales.

    _OPP_ENERGY_NOISE: float = 1.0  # Was 1.5
    _OPP_ENERGY_FILTER_SCALE: float = 16 / 14 * 1.75
    _OPP_ENERGY_POOL_SCALE: float = 1.75

    # Clutter coefficients to compute final feature congestion map
    _COLOR_COEF: float = 0.2088
    _CONTRAST_COEF: float = 0.0660
    _ORIENTATION_COEF: float = 0.0269
    _MINKOWSKI_ORDER: float = (
        1.0  # a parameter when combining local clutter over space
    )

    # empty luminance (lum) and chrominance (a,b) channels
    _lum_pyr: Dict = {}
    _a_pyr: Dict = {}
    _b_pyr: Dict = {}

    # private methods
    @staticmethod
    def _collapse(clutter_levels: List) -> np.ndarray:
        """
        Collapse over scales by taking the maximum.

        First get a Gaussian kernel to up-sample the clutter maps on bigger scales
        so that the clutter maps would have the same sizes, and max can be taken
        across scales.

        Args:
            clutter_levels: list of clutter levels

        Returns:
            Collapsed clutter map
        """
        # kernel approximation for the five - tap 1D Gaussian filter used in pyramid methods for image processing
        kernel_1d: np.ndarray = np.array([[0.05, 0.25, 0.4, 0.25, 0.05]])
        kernel_2d: np.ndarray = conv2(kernel_1d, kernel_1d.T)

        clutter_map: np.ndarray = clutter_levels[0].copy()
        for scale in range(1, len(clutter_levels)):
            clutter_here: np.ndarray = clutter_levels[scale]

            for kk in range(scale, 0, -1):
                clutter_here = upConv(
                    image=clutter_here,
                    filt=kernel_2d,
                    edge_type="reflect1",
                    step=[2, 2],
                    start=[0, 0],
                )

            common_sz = min(clutter_map.shape[0], clutter_here.shape[0]), min(
                clutter_map.shape[1], clutter_here.shape[1]
            )
            for i in range(0, common_sz[0]):
                for j in range(0, common_sz[1]):
                    clutter_map[i][j] = max(
                        clutter_map[i][j], clutter_here[i][j]
                    )

        return clutter_map

    @classmethod
    def _color_clutter(cls) -> np.ndarray:
        """
        Compute the color clutter map of an image.

        Color clutter is computed as the "volume" of a color distribution
        ellipsoid, which is the determinant of covariance matrix. Covariance
        matrix can be computed efficiently through linear filtering. More
        specifically, cov(X,Y) = E(XY)-E(X)E(Y), where E (expectation value)
        can be approximated by filtering with a Gaussian window.

        Returns:
            Results
            - color_clutter_map (ndarray): an array of the same size as inputImage
        """
        # Initialization
        covMx: Dict = {}
        color_clutter_levels = [0] * cls._LEVELS
        DL: list = [0] * cls._LEVELS
        Da: list = [0] * cls._LEVELS
        Db: list = [0] * cls._LEVELS

        # Sensitivitis to the L, a, and b channels are different, therefore we use
        # deltaL2, deltaa2, and deltab2 to "scale" the L, a, and b axes when computing
        # the covariance matrix. Eventually these numbers should be vary according
        # to the spatial scales, mimicing our visual system's sensitivity function.
        deltaL2: float = 0.0007 ** 2
        deltaa2: float = 0.1 ** 2
        deltab2: float = 0.05 ** 2

        # Get a Gaussian filter for computing the covariance
        bigG: np.ndarray = RRgaussfilter1D(
            round(2 * cls._COLOR_POOL_SIGMA), cls._COLOR_POOL_SIGMA
        )

        for i in range(0, cls._LEVELS):
            # Get E(X) by filtering X with a one-dimensional Gaussian window separably in x and y directions:
            DL[i] = RRoverlapconv(bigG, cls._lum_pyr[(i, 0)])
            DL[i] = RRoverlapconv(bigG.T, DL[i])  # E(L)
            Da[i] = RRoverlapconv(bigG, cls._a_pyr[(i, 0)])
            Da[i] = RRoverlapconv(bigG.T, Da[i])  # E(a)
            Db[i] = RRoverlapconv(bigG, cls._b_pyr[(i, 0)])
            Db[i] = RRoverlapconv(bigG.T, Db[i])  # E(b)

            # Covariance matrix
            # covMx(L,a,b) = | cov(L,L)  cov(L,a)  cov(L,b) |
            #                | cov(a,L)  cov(a,a)  cov(a,b) |
            #                | cov(b,L)  cov(b,a)  cov(b,b) |
            # where cov(X,Y) = E(XY) - E(X)E(Y)
            #   and if X is the same as Y, then it's the variance var(X) =
            #   E(X.^2)-E(X).^2
            # and as cov(X,Y) = cov(Y,X), covMx is symmetric

            # covariance matrix elements:
            covMx[(i, 0, 0)] = RRoverlapconv(bigG, cls._lum_pyr[(i, 0)] ** 2)
            covMx[(i, 0, 0)] = (
                    RRoverlapconv(bigG.T, covMx[(i, 0, 0)]) - DL[i] ** 2 + deltaL2
            )  # cov(L,L) + deltaL2
            covMx[(i, 0, 1)] = RRoverlapconv(
                bigG, cls._lum_pyr[(i, 0)] * cls._a_pyr[(i, 0)]
            )
            covMx[(i, 0, 1)] = (
                    RRoverlapconv(bigG.T, covMx[(i, 0, 1)]) - DL[i] * Da[i]
            )  # cov(L,a)
            covMx[(i, 0, 2)] = RRoverlapconv(
                bigG, cls._lum_pyr[(i, 0)] * cls._b_pyr[(i, 0)]
            )
            covMx[(i, 0, 2)] = (
                    RRoverlapconv(bigG.T, covMx[(i, 0, 2)]) - DL[i] * Db[i]
            )  # cov(L,b)
            covMx[(i, 1, 1)] = RRoverlapconv(bigG, cls._a_pyr[(i, 0)] ** 2)
            covMx[(i, 1, 1)] = (
                    RRoverlapconv(bigG.T, covMx[(i, 1, 1)]) - Da[i] ** 2 + deltaa2
            )  # cov(a,a) + deltaa2
            covMx[(i, 1, 2)] = RRoverlapconv(
                bigG, cls._a_pyr[(i, 0)] * cls._b_pyr[(i, 0)]
            )
            covMx[(i, 1, 2)] = (
                    RRoverlapconv(bigG.T, covMx[(i, 1, 2)]) - Da[i] * Db[i]
            )  # cov(a,b)
            covMx[(i, 2, 2)] = RRoverlapconv(bigG, cls._b_pyr[(i, 0)] ** 2)
            covMx[(i, 2, 2)] = (
                    RRoverlapconv(bigG.T, covMx[(i, 2, 2)]) - Db[i] ** 2 + deltab2
            )
            # cov(b,b) + deltab2

            # Get the determinant of covariance matrix
            # which is the "volume" of the covariance ellipsoid
            detIm = (
                    covMx[(i, 0, 0)]
                    * (
                            covMx[(i, 1, 1)] * covMx[(i, 2, 2)]
                            - covMx[(i, 1, 2)] * covMx[(i, 1, 2)]
                    )
                    - covMx[(i, 0, 1)]
                    * (
                            covMx[(i, 0, 1)] * covMx[(i, 2, 2)]
                            - covMx[(i, 1, 2)] * covMx[(i, 0, 2)]
                    )
                    + covMx[(i, 0, 2)]
                    * (
                            covMx[(i, 0, 1)] * covMx[(i, 1, 2)]
                            - covMx[(i, 1, 1)] * covMx[(i, 0, 2)]
                    )
            )

            # Take the square root considering variance is squared, and the cube
            # root, since this is the volume and the contrast measure is a "length"
            color_clutter_levels[i] = np.sqrt(detIm) ** (1 / 3)

        # Compute color clutter map
        color_clutter_map = cls._collapse(color_clutter_levels)

        return color_clutter_map

    @classmethod
    def _contrast_clutter(cls) -> np.ndarray:
        """
        Computes the contrast clutter map of an image.

         Returns:
            Results
            - contrast_clutter_map (ndarray): an array of the same size as inputImage
        """
        # Compute a form of "contrast-energy" by filtering the luminance
        # channel L by a center-surround filter and squaring (or taking the absolute
        # values of) the filter outputs. The center-surround filter is a DoG1 filter
        # with std '_CONTRAST_FILT_SIGMA'.
        contrast = RRcontrast1channel(cls._lum_pyr, 1)

        # Initiate clutter_map and clutter_levels
        contrast_clutter_levels = [0] * cls._LEVELS

        # Get a Gaussian filter for computing the variance of contrast.
        # Since we used a Gaussian pyramid to find contrast features, these filters
        # have the same size regardless of the scale of processing.
        bigG = RRgaussfilter1D(round(6), 3)

        for scale in range(0, cls._LEVELS):
            # var(X) = E(X.^2) - E(X).^2
            # Get E(X) by filtering X with a one-dimensional Gaussian window separably in x and y directions
            meanD = RRoverlapconv(bigG, contrast[scale])
            meanD = RRoverlapconv(bigG.T, meanD)

            # Get E(X.^2) by filtering X.^2 with a one-dimensional Gaussian window separably in x and y directions
            meanD2 = RRoverlapconv(bigG, contrast[scale] ** 2)
            meanD2 = RRoverlapconv(bigG.T, meanD2)

            # Get variance by var(X) = E(X.^2) - E(X).^2
            stddevD = np.sqrt(abs(meanD2 - meanD ** 2))
            contrast_clutter_levels[scale] = stddevD

        contrast_clutter_map = cls._collapse(contrast_clutter_levels)

        return contrast_clutter_map

    @classmethod
    def _rr_orientation_opp_energy(cls) -> list:
        """
        OPP_ENERGY: This runs the oriented opponent energy calculation that
        serves as the first stages in Bergen & Landy's (1990) texture segmentor,
        except it uses DOOG filters (which actually don't work as well, but at
        least we can more easily control the scale).
        """
        hvdd: list = [0] * cls._LEVELS
        hv: list = [0] * cls._LEVELS
        dd: list = [0] * cls._LEVELS
        out: list = [0] * cls._LEVELS
        total: list = [0] * cls._LEVELS

        for scale in range(0, cls._LEVELS):
            # Check this is the right order for Landy/Bergen. RRR
            hvdd[scale] = orient_filtnew(
                cls._lum_pyr[(scale, 0)], cls._OPP_ENERGY_FILTER_SCALE
            )

            # Filter with 4 oriented filters 0, 45, 90, 135. Was sigma = 16/14, orient_filtnew,
            # then 16/14*1.75 to match contrast and other scales.
            # Eventually make this sigma a variable that's passed to this routine.
            # hvdd[scale] is the 4 output images concatenated together,
            # in the order horizontal, vertical, up-left, and down-right.
            hvdd[scale] = [x ** 2 for x in hvdd[scale]]  # local energy
            hvdd[scale] = poolnew(
                hvdd[scale], cls._OPP_ENERGY_POOL_SCALE
            )  # Pools with a gaussian filter. Was effectively sigma=1, then 1.75 to match 1.75 above.

            # RRR Should look at these results and see if this is the right amount of pooling for the new filters.
            hv[scale] = HV(hvdd[scale])  # get the difference image between horizontal and vertical: H-V (0-90)
            dd[scale] = DD(hvdd[scale])  # get the difference image between right and left: R-L (45-135)

            # Normalize by the total response at this scale, assuming the total
            # response is high enough. If it's too low, we'll never see this
            # orientation. I'm not sure what to do here -- set it to zeros and
            # it's like that's the orientation. Maybe output the total response
            # and decide what to do later. RRR
            total[scale] = (
                    sumorients(hvdd[scale]) + cls._OPP_ENERGY_NOISE
            )  # add noise based upon sumorients at visibility threshold
            hv[scale] = (hv[scale] / total[scale])  # normalize the hv and dd image
            dd[scale] = dd[scale] / total[scale]
            out[scale] = (
                hv[scale],
                dd[scale],
            )  # out is the 2 output images concatenated together, in the order of hv, dd

        return out

    @classmethod
    def _orientation_clutter(cls) -> np.ndarray:
        """
        Compute the orientation clutter map of an image.

        Orientation clutter is computed as the "volume" of an orientation distribution
        ellipsoid, which is the determinant of covariance matrix. Treats cos(2 theta)
        and sin(2 theta) (computed from OrientedOppEnergy) as a two-vector, and gets
        The covariance of this two-vector. The covariance matrix can be computed
        efficiently through linear filtering. More specifically, cov(X,Y) = E(XY)-E(X)E(Y),
        where E (expectation value) can be approximated by filtering with a Gaussian window.
        poolScale is set to 7/2.

        This currently seems far too dependent on luminance contrast. Check into
        why this is so -- I thought we were normalizing by local contrast.

        Returns:
            Results
            - orientation_clutter_map (ndarray): an array of the same size as inputImage
        """
        Dc: list = [0] * cls._LEVELS  # mean "cos 2 theta" at distractor scale
        Ds: list = [0] * cls._LEVELS  # mean "sin 2 theta" at distractor scale

        # Get approximations to cos(2theta) and sin(2theta) from oriented opponent
        # energy, at each of the numlevels of the pyramid
        angles = cls._rr_orientation_opp_energy()

        # Compute the two-vector [meancos, meansin] at each scale, as well as the
        # things we need to compute the mean and covariance of this two-vector at
        # the larger, distractor scale.
        bigG = RRgaussfilter1D(round(8 * cls._ORIENTATION_POOL_SIGMA), 4 * cls._ORIENTATION_POOL_SIGMA)

        covMx: Dict = {}
        orientation_clutter_levels = [0] * cls._LEVELS

        for i in range(0, cls._LEVELS):
            cmx = angles[i][0]
            smx = angles[i][1]

            # Pool to get means at distractor scale. In pooling, don't pool
            # over the target region (implement this by pooling with a big
            # Gaussian, then subtracting the pooling over the target region
            # computed above. Note, however, that we first need to scale the
            # target region pooling so that its peak is the same height as
            # this much broader Gaussian used to pool over the distractor
            # region.
            Dc[i] = RRoverlapconv(bigG, cmx)
            Dc[i] = RRoverlapconv(bigG.T, Dc[i])
            Ds[i] = RRoverlapconv(bigG, smx)
            Ds[i] = RRoverlapconv(bigG.T, Ds[i])

            # Covariance matrix elements. Compare with computations in
            # RRStatisticalSaliency. I tried to match computeColorClutter, but I
            # don't remember the meaning of some of the terms I removed.  XXX
            covMx[(i, 0, 0)] = RRoverlapconv(bigG, cmx ** 2)
            covMx[(i, 0, 0)] = (
                    RRoverlapconv(bigG.T, covMx[(i, 0, 0)])
                    - Dc[i] ** 2
                    + cls._ORIENTATION_NOISE
            )
            covMx[(i, 0, 1)] = RRoverlapconv(bigG, cmx * smx)
            covMx[(i, 0, 1)] = (
                    RRoverlapconv(bigG.T, covMx[(i, 0, 1)]) - Dc[i] * Ds[i]
            )
            covMx[(i, 1, 1)] = RRoverlapconv(bigG, smx ** 2)
            covMx[(i, 1, 1)] = (
                    RRoverlapconv(bigG.T, covMx[(i, 1, 1)])
                    - Ds[i] ** 2
                    + cls._ORIENTATION_NOISE
            )

            # Get determinant of covariance matrix, which is the volume of the
            # covariance ellipse
            detIm = covMx[(i, 0, 0)] * covMx[(i, 1, 1)] - covMx[(i, 0, 1)] ** 2
            # Take the square root considering variance is squared, and the square
            # root again, since this is the area and the contrast measure is a "length"
            orientation_clutter_levels[i] = detIm ** (1 / 4)

        # Compute orientation clutter map
        orientation_clutter_map = cls._collapse(orientation_clutter_levels)
        return orientation_clutter_map

    @classmethod
    def execute(
            cls,
            pil_image: Optional[Image.Image] = None,
            lab_image: Optional[np.ndarray] = None,
            image_url: Optional[HttpUrl] = None,
            grayscale_image: Optional[Image.Image] = None,
            png_image: Optional[BytesIO] = None,
            jpeg_image: Optional[BytesIO] = None,
            segments: Optional[Dict[str, Any]] = None,
            dom_analysis_result: Optional[Dict[str, Any]] = None,
    ) -> Optional[List[Union[int, str, float, Image.Image]]]:

        # Split CIELab color space image to the luminance (lum) and chrominance (a,b) channels
        lum: np.ndarray = lab_image[:, :, 0]
        a: np.ndarray = lab_image[:, :, 1]
        b: np.ndarray = lab_image[:, :, 2]

        # Get Gaussian pyramids (one for each of L,a,b)
        pyr = pyramids.GaussianPyramid(lum, height=cls._LEVELS)
        cls._lum_pyr = pyr.pyr_coeffs
        pyr = pyramids.GaussianPyramid(a, height=cls._LEVELS)
        cls._a_pyr = pyr.pyr_coeffs
        pyr = pyramids.GaussianPyramid(b, height=cls._LEVELS)
        cls._b_pyr = pyr.pyr_coeffs

        # Compute the clutters: color, contrast, and orientation
        color_clutter_map: np.ndarray = cls._color_clutter()
        print("color clutter map completed")
        orientation_clutter_map: np.ndarray = cls._orientation_clutter()
        print("orientation clutter map completed")
        contrast_clutter_map: np.ndarray = cls._contrast_clutter()
        print("contrast clutter map completed")

        # Compute the feature congestion measure of visual clutter
        # Combine color, contrast, and orientation clutters
        clutter_map_fc: np.ndarray = (
                color_clutter_map / cls._COLOR_COEF
                + contrast_clutter_map / cls._CONTRAST_COEF
                + orientation_clutter_map / cls._ORIENTATION_COEF
        )

        print("combined clutter map completed")

        # Combine over space using a Minkowski mean of order "_MINKOWSKI_ORDER", then take the average element wise
        clutter_scalar_fc: float = float(
            np.mean(clutter_map_fc ** cls._MINKOWSKI_ORDER)
            ** (1 / cls._MINKOWSKI_ORDER)
        )

        # Normalize output image
        clutter_array_fc: np.ndarray = normalize(clutter_map_fc)
        clutter_image_fc: Image.Image = Image.fromarray(clutter_array_fc)

        # convert PIL edge image to PNG
        buf = BytesIO()
        clutter_image_fc.save(buf, format="PNG")

        return [
            clutter_scalar_fc,
            buf,
        ]
