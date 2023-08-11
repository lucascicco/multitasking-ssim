import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim


class ImageCalculations:
    @staticmethod
    def mse(image1: np.ndarray, image2: np.ndarray) -> float:
        """Calculate the Mean Squared Error (MSE) between two grayscale images.

        Args:
        ----
            image1 (np.ndarray): Grayscale image 1.
            image2 (np.ndarray): Grayscale image 2.

        Returns:
        -------
            float: The Mean Squared Error value.
        """
        h, w = image1.shape
        diff = cv2.absdiff(image1, image2)
        error = np.sum(diff**2)
        return error / float(h * w)

    @staticmethod
    def ssim(image1: np.ndarray, image2: np.ndarray) -> float:
        """Calculate the Structural Similarity Index (SSIM) between two grayscale images.

        Args:
        ----
            image1 (np.ndarray): Grayscale image 1.
            image2 (np.ndarray): Grayscale image 2.

        Returns:
        -------
            float: The SSIM value.
        """
        return ssim(image1, image2)

    @staticmethod
    def psnr(image1: np.ndarray, image2: np.ndarray) -> float:
        """Calculate the Peak Signal-to-Noise Ratio (PSNR) between two grayscale images.

        Args:
        ----
            image1 (np.ndarray): Grayscale image 1.
            image2 (np.ndarray): Grayscale image 2.

        Returns:
        -------
            float: The PSNR value.
        """
        h, w = image1.shape
        diff = cv2.absdiff(image1, image2)
        error = np.sum(diff**2)
        mse = error / float(h * w)
        if mse == 0:
            # Images are identical, PSNR is undefined. Set a high value for similarity.
            return float("inf")
        max_pixel = 255.0  # Assuming pixel values are in the range [0, 255]
        return 20 * np.log10(max_pixel / np.sqrt(mse))
