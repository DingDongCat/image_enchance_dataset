import time

import torch
import numpy as np
from app.model.meta_model.SID_raw import *
from app.model.meta_model.isp_new import *
import skimage.metrics


def test_SID(model_path='app/model/pretrained_model/500_G.pth',
             image_path='app/model/data/0009_U3_3200_10.CR2', gt_path=None):
    model = SeeInDark()
    model.cuda()
    model.eval()
    model_info = torch.load(model_path)
    model.load_state_dict(model_info)

    with rawpy.imread(image_path) as raw:
        img = pack_raw_bayer(raw)
        wb, ccm = read_wb_ccm(raw)

    input_image = np.expand_dims(img[:, :256, :256], axis=0)
    input_var = torch.from_numpy(input_image).float().to("cuda:0")

    start_time = time.time()
    with torch.no_grad():
        output = model(input_var)
    end_time = time.time()
    elapsed_time = end_time - start_time
    # print(output.shape)

    output = output.squeeze(0)
    output = output.cpu().numpy()
    if gt_path:
        with rawpy.imread(gt_path) as raw:
            gt_img = pack_raw_bayer(raw)
            # wb, ccm = read_wb_ccm(raw)
            gt_img = gt_img[:, :256, :256]
        ssim = skimage.metrics.structural_similarity(gt_img, output, data_range=1, channel_axis=0)
        psnr = skimage.metrics.peak_signal_noise_ratio(gt_img, output)
        # print(ssim, psnr)
    # print(output.shape)
    output = raw2rgb_v2(output, wb, ccm).transpose(1, 2, 0)
    output = output[:, :, (2, 1, 0)] * 255
    # save_img(output, "test.jpg")
    if gt_path:
        return output, int(elapsed_time * 1000), psnr, ssim.astype(np.float64)
    else:
        return output, int(elapsed_time * 1000)

