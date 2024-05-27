import asyncio
import datetime
import os.path
import time

from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtGui import QImage, QPixmap, QColor
import numpy as np
from PyQt5.QtWidgets import QMessageBox

from ..common.config import cfg
import cv2

import rawpy
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


#


# def get_matrix(self):
#     # 获取标签上显示的图片
#     pixmap = self.label.pixmap()
#
#     if pixmap:
#         # 将图片转换为 QImage 对象
#         image = pixmap.toImage()
#
#         # 获取图片的尺寸
#         width = image.width()
#         height = image.height()
#
#         # 获取图片的通道数
#         channel_count = 3  # 假设为彩色图像，通道数为3 (RGB)
#
#         # 创建一个三维数组来存储像素值
#         matrix = np.zeros((channel_count, height, width), dtype=np.uint8)
#
#         # 遍历图片的每个像素，并将像素颜色值转换为c * w * h矩阵
#         for y in range(height):
#             for x in range(width):
#                 color = QColor(image.pixelColor(x, y))
#                 matrix[0, y, x] = color.red()  # 红色通道
#                 matrix[1, y, x] = color.green()  # 绿色通道
#                 matrix[2, y, x] = color.blue()  # 蓝色通道
#
#         # 输出矩阵
#         print(matrix.shape)

class SignalCenter(QObject):
    pixmap_signal = pyqtSignal(QPixmap)
    test_finished_signal = pyqtSignal(str)
    update_list_view_signal = pyqtSignal(list)
    file_name = ""
    model_name = ""
    elapsed_time = ""
    psnr = 0.
    ssim = 0.
    list_result = []

    def start_test(self, model_path, image_path, gt_file_path=None):
        from app.model.test import test_SID
        print("signal get")
        self.file_name = image_path
        self.model_name = model_path
        if gt_file_path:
            result, elapsed_time, self.psnr, self.ssim = test_SID(model_path, image_path, gt_path=gt_file_path)
        else:
            self.psnr = 0.
            self.ssim = 0.
            result, elapsed_time = test_SID(model_path, image_path, gt_path=gt_file_path)
        self.elapsed_time = "{}".format(elapsed_time)
        self.save_img(result)
        # print("程序运行时间：{} ms".format(elapsed_time))
        result = result.astype(np.uint8)
        # print(result.shape, result, result.dtype)
        res_shape = result.shape
        result = result[:, :, ::-1]
        image = QImage(result.data.tobytes(), res_shape[0], res_shape[1], 3 * res_shape[1], QImage.Format_RGB888)

        pixmap = QPixmap.fromImage(image)

        # self.label.setPixmap(pixmap)
        # print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "test success")
        self.pixmap_signal.emit(pixmap)
        return pixmap

    def save_img(self, img):
        # print(self.model_name, self.file_name)
        self.model_name = self.model_name.split(".")[0].split("/")[-1]
        self.file_name = ".".join(self.file_name.split(".")[0:-1]).split("/")[-1]
        name_arr = []
        # print(self.model_name, self.file_name)
        name_arr.append(self.model_name)
        name_arr.append(self.file_name)
        name_arr.append("{}".format(self.elapsed_time))
        name_arr.append("{:.2f}".format(self.psnr))
        name_arr.append("{:.4f}".format(self.ssim))
        # name_arr.append(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        # print("#".join(name_arr))
        img_path = cfg.downloadFolder.value + "/" + "#".join(name_arr) + ".png"
        print(img_path)
        print(img.shape)
        success = cv2.imwrite(img_path, img)
        print(success)

    def start_multi_image_test(self, test_config):
        gt_file = test_config["gt_file"]
        model_path = test_config["pretrained_model"]
        test_file_list = test_config["test_file_list"]

        try:
            for test_file in test_file_list:
                self.start_single_image_test(model_path=model_path, test_file=test_file, gt_path=gt_file)
            self.update_list_view_signal.emit(self.list_result)
            self.test_finished_signal.emit(f"Success")
        except Exception as e:
            print(e)
            self.test_finished_signal.emit(f"Unexpected error: {e}")

    def start_single_image_test(self, model_path, test_file, gt_path=None):
        from app.model.test import test_SID
        self.file_name = test_file
        self.model_name = model_path
        result, self.elapsed_time, self.psnr, self.ssim = test_SID(model_path, test_file, gt_path=gt_path)
        # add code to modify file name
        # print(result.shape)
        self.list_result.append([
            self.model_name.split(".")[0].split("/")[-1],
            ".".join(self.file_name.split(".")[0:-1]).split("/")[-1],
            "{}".format(self.elapsed_time),
            "{:.2f}".format(self.psnr),
            "{:.4f}".format(self.ssim)
        ])
        self.save_img(result)


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
    print(wbs.shape)
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


def save_img(img, img_path, mode='RGB'):
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
