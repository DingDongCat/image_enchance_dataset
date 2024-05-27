import rawpy
import numpy as np
import cv2
import matplotlib.pyplot as plt
from PIL import Image
import exifread
import torch
import rawpy
import os
from os.path import join
import scipy.stats as stats
from hdf5storage import loadmat, savemat

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")


def apply_gains(bayer_images, wbs):
    """Applies white balance to a batch of Bayer images."""
    N, C, _, _ = bayer_images.shape
    outs = bayer_images * wbs.view(N, C, 1, 1)
    # outs = bayer_images * wbs.view(N, C)
    return outs


def apply_ccms(images, ccms):
    """Applies color correction matrices."""
    images = images.permute(
        0, 2, 3, 1)  # Permute the image tensor to BxHxWxC format from BxCxHxW format
    images = images[:, :, :, None, :]
    ccms = ccms[:, None, None, :, :]
    outs = torch.sum(images * ccms, dim=-1)
    # Re-Permute the tensor back to BxCxHxW format
    outs = outs.permute(0, 3, 1, 2)
    return outs


def gamma_compression(images, gamma=2.2):
    """Converts from linear to gamma space."""
    outs = torch.clamp(images, min=1e-8) ** (1 / gamma)
    # outs = (1 + gamma[0]) * np.power(images, 1.0/gamma[1]) - gamma[0] + gamma[2]*images
    outs = torch.clamp((outs * 255).int(), min=0, max=255).float() / 255
    return outs


def binning(bayer_images):
    """RGBG -> RGB"""
    lin_rgb = torch.stack([
        bayer_images[:, 0, ...],
        torch.mean(bayer_images[:, [1, 3], ...], dim=1),
        bayer_images[:, 2, ...]], dim=1)

    return lin_rgb


def process(bayer_images, wbs, cam2rgbs, gamma=2.2, CRF=None):
    """Processes a batch of Bayer RGBG images into sRGB images."""
    # White balance.
    bayer_images = apply_gains(bayer_images, wbs)
    # Binning
    bayer_images = torch.clamp(bayer_images, min=0.0, max=1.0)
    images = binning(bayer_images)
    # Color correction.
    images = apply_ccms(images, cam2rgbs)
    # Gamma compression.
    images = torch.clamp(images, min=0.0, max=1.0)
    if CRF is None:
        images = gamma_compression(images, gamma)
    # else:
    #     images = camera_response_function(images, CRF)

    return images


def raw2rgb_v2(packed_raw, wb, ccm, CRF=None, gamma=2.2):  # RGBG
    packed_raw = torch.from_numpy(packed_raw).float()
    wb = torch.from_numpy(wb).float()
    cam2rgb = torch.from_numpy(ccm).float()
    out = process(packed_raw[None], wbs=wb[None], cam2rgbs=cam2rgb[None], gamma=gamma, CRF=CRF)[0, ...].numpy()
    return out


def raw2rgb_v3(packed_raw, wb, ccm, CRF=None, gamma=2.2):  # RGBG
    packed_raw = torch.from_numpy(packed_raw).float()
    out = process(packed_raw[None], wbs=wb[None], cam2rgbs=ccm[None], gamma=gamma, CRF=CRF)[0, ...].numpy()
    return out


def read_wb_ccm(raw):
    wb = np.array(raw.camera_whitebalance)
    wb /= wb[1]
    wb[3] = 1.0
    wb = wb.astype(np.float32)
    ccm = raw.rgb_xyz_matrix[:3, :3].astype(np.float32)
    return wb, ccm


# 正常数据
def ISP(data, raw):
    wb, ccm = read_wb_ccm(raw)
    # print(wb, ccm)
    img = raw2rgb_v2(data, wb, ccm).transpose(1, 2, 0)
    return img


def save_img(img, img_path, mode='BGR'):
    cv2.imwrite(img_path, img)


def pack_raw_bayer(raw):
    # pack Bayer image to 4 channels
    im = raw.raw_image_visible.astype(np.float32)
    raw_pattern = raw.raw_pattern
    R = np.where(raw_pattern == 0)
    G1 = np.where(raw_pattern == 1)
    B = np.where(raw_pattern == 2)
    G2 = np.where(raw_pattern == 3)

    white_level = raw.white_level

    img_shape = im.shape
    H = img_shape[0] - img_shape[0] % 2
    W = img_shape[1] - img_shape[1] % 2

    out = np.stack((im[R[0][0]:H:2, R[1][0]:W:2],  # RGBG
                    im[G1[0][0]:H:2, G1[1][0]:W:2],
                    im[B[0][0]:H:2, B[1][0]:W:2],
                    im[G2[0][0]:H:2, G2[1][0]:W:2]), axis=0).astype(np.float32)

    black_level = np.array(raw.black_level_per_channel)[:, None, None].astype(np.float32)

    out = (out - black_level) / (white_level - black_level)
    out = np.clip(out, 0, 1)

    return out
