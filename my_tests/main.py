from os.path import isfile, splitext
from plenopticam.cfg import PlenopticamConfig
from plenopticam.misc.status import PlenopticamStatus
from plenopticam import lfp_reader
from plenopticam import lfp_calibrator
from plenopticam import lfp_aligner
from plenopticam import lfp_extractor
import cv2

lfp_path = "my_tests/toy.lfr"
cal_path = "my_tests/MOD_0015.RAW"
lfp_img = None
wht_img = None
lfp_img_align = None
vp_img_arr = None
lfp_img_align = None
cfg = PlenopticamConfig()
sta = PlenopticamStatus()

def main():
    global wht_img, lfp_img, lfp_img_align, vp_img_arr, cfg, sta
    load_lfp(lfp_path=lfp_path, wht_opt=False)
    # auto_find()
    load_lfp(lfp_path=cal_path, wht_opt=True)
    cal()
    cfg.load_cal_data()
    lfp_align()
    lfp_extract()
    
    wht_img = wht_img * 255.0
    lfp_img = lfp_img * 255.0
    cv2.imwrite("my_tests/wht_img.png", wht_img)
    cv2.imwrite("my_tests/lfp_img.png", lfp_img)
    cv2.imwrite("my_tests/lfp_img_align.png", lfp_img_align)

def load_lfp(lfp_path=None, wht_opt=False):
    global lfp_img, wht_img, sta, cfg
    # decode light field image
    lfp_obj = lfp_reader.LfpReader(cfg=cfg, sta=sta, lfp_path=lfp_path)
    lfp_obj.main()
    if wht_opt:
        wht_img = lfp_obj.lfp_img
    else:
        lfp_img = lfp_obj.lfp_img
    del lfp_obj
    
def auto_find():
    global wht_img
    if wht_img is None:
        # find calibration file automatically
        obj = lfp_calibrator.CaliFinder(cfg)
        obj.main()
        wht_img = obj._wht_bay
        del obj

    # white image demosaicing (when light field image is given as RGB)
    if wht_img is not None and len(lfp_img.shape) == 3:
        from plenopticam.lfp_aligner.cfa_processor import CfaProcessor
        cfa_obj = CfaProcessor(bay_img=wht_img, cfg=cfg)
        cfa_obj.bay2rgb()
        wht_img = cfa_obj.rgb_img
        del cfa_obj

def cal():
    global cfg, wht_img, sta
    # perform centroid calibration
    cal_obj = lfp_calibrator.LfpCalibrator(wht_img=wht_img, sta=sta, cfg=cfg)
    cal_obj.main()
    cfg = cal_obj.cfg
    del cal_obj

def lfp_align():
    global lfp_img, wht_img, lfp_img_align, cfg, sta
    # align light field
    lfp_obj = lfp_aligner.LfpAligner(lfp_img=lfp_img, cfg=cfg, sta=sta, wht_img=wht_img)
    lfp_obj.main()
    lfp_img_align = lfp_obj.lfp_img
    del lfp_obj
     
def lfp_extract():
    global cfg, lfp_img_align, vp_img_arr, sta
    # export light field data
    exp_obj = lfp_extractor.LfpExtractor(lfp_img_align=lfp_img_align, cfg=cfg, sta=sta)
    exp_obj.main()
    vp_img_arr = exp_obj.vp_img_linear
    del exp_obj

if __name__ == "__main__":
    main()