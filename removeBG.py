########################################################
# Remove Background / 移除背景
#
# History:
# When      | Who         | What
# 2024/09/21| - TQ Ye     |
########################################################
from rembg import remove
from PIL import Image
import os

def remove_bg(inImgFile, outImpFile):
    """
    Remove Background /移除背景
    :param inImgFile: input image file / 输入图片文件
    :param outImpFile: output image file / 输出图片文件
    """

    #check file exist
    if not os.path.exists(inImgFile):
        print(f"Error: {inImgFile} not found")
        return

    input = Image.open(inImgFile)
    output = remove(input)
    output.save(outImpFile)


##################### Main ###############################
if __name__ == "__main__":

    # input image file / 输入图片文件
    inImgFile = "input_image.jpg"
    # output image file / 输出图片文件
    outImpFile = "output_image.png"
    # Call remove_bg
    remove_bg(inImgFile, outImpFile)

########################################################

